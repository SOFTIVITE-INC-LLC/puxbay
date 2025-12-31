import json
import uuid
from django.db import transaction
from django.shortcuts import get_object_or_404
from main.models import Product, Customer, Order, OrderItem
from accounts.models import Branch, UserProfile
from branches.models import StockMovement
from utils.identifier_generator import generate_order_number, generate_item_number

class POSService:
    def __init__(self, tenant, user_profile=None):
        self.tenant = tenant
        self.user_profile = user_profile

    def get_pos_data(self, branch):
        """
        Retrieves and serializes all data needed for the POS interface.
        """
        from main.models import Product, Customer, Category
        from storefront.models import StorefrontSettings
        import json

        products = Product.objects.filter(branch=branch, is_active=True, stock_quantity__gte=0).select_related('category')
        categories = Category.objects.filter(branch=branch)
        customers = Customer.objects.filter(tenant=self.tenant)
        
        # Serialize products
        products_json = []
        for p in products:
            products_json.append({
                'id': str(p.id),
                'name': p.name,
                'price': float(p.price),
                'wholesale_price': float(p.wholesale_price),
                'stock': p.stock_quantity,
                'sku': p.sku,
                'category': p.category.name if p.category else 'Uncategorized',
                'category_id': str(p.category.id) if p.category else 0,
                'image_url': p.image_url
            })
            
        # Serialize customers
        customers_json = []
        for c in customers:
            customers_json.append({
                'id': str(c.id),
                'name': c.name,
                'phone': c.phone or '',
                'email': c.email or '',
                'customer_type': c.customer_type,
                'loyalty_points': float(c.loyalty_points),
                'store_credit': float(c.store_credit_balance),
                'credit_limit': float(c.credit_limit),
                'outstanding_debt': float(c.outstanding_debt)
            })

        # Serialize categories
        categories_json = []
        for c in categories:
            categories_json.append({
                'id': str(c.id),
                'name': c.name
            })

        # Fetch Payment Settings
        store_settings = StorefrontSettings.objects.filter(tenant=self.tenant).first()
        
        payment_config = {
            'stripe_enabled': False,
            'stripe_key': None,
            'paystack_enabled': False,
            'paystack_key': None,
            'currency_code': branch.currency_code,
            'logo_url': branch.logo.url if branch.logo else None
        }
        
        if store_settings:
            if store_settings.enable_stripe and store_settings.stripe_public_key:
                payment_config['stripe_enabled'] = True
                payment_config['stripe_key'] = store_settings.stripe_public_key
                
            if store_settings.enable_paystack and store_settings.paystack_public_key:
                payment_config['paystack_enabled'] = True
                payment_config['paystack_key'] = store_settings.paystack_public_key

        return {
            'products': products_json,
            'customers': customers_json,
            'categories': categories_json,
            'payment_config': payment_config,
            'branch_id': str(branch.id),
            'branch_name': branch.name
        }

    def void_order(self, order_id):
        """
        Voids an order, restores stock, and updates status.
        """
        from django.db import transaction
        
        try:
            with transaction.atomic():
                order = Order.objects.get(pk=order_id, tenant=self.tenant)
                if order.status == 'cancelled':
                    return {'status': 'info', 'message': 'Order already voided'}
                
                # Restore Stock only if it was previously deducted (status was 'completed')
                if order.status == 'completed':
                    for item in order.items.all():
                        if item.product:
                            item.product.stock_quantity += item.quantity
                            item.product.save()
                            # Log movement
                            self._log_movement(item.product, item.quantity, order, order.branch)
                
                order.status = 'cancelled'
                order.save()
                
                return {'status': 'success', 'message': 'Order voided successfully'}
        except Order.DoesNotExist:
            return {'status': 'error', 'message': 'Order not found'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def complete_pending_order(self, order_id):
        """
        Marks a pending order as completed and deducts inventory.
        """
        try:
            with transaction.atomic():
                order = Order.objects.get(pk=order_id, tenant=self.tenant, status='pending')
                
                # 1. Update Status & Cashier
                order.status = 'completed'
                if self.user_profile:
                    order.cashier = self.user_profile
                order.save()
                
                # 2. Deduct Inventory (Skip for online orders as they deduct at creation)
                if order.ordering_type != 'online':
                    for item in order.items.all():
                        if item.product:
                            self._deduct_stock(item.product, item.quantity, order, order.branch)
                    print(f"[POSService] Stock deducted for {order.ordering_type} order {order.order_number}")
                else:
                    print(f"[POSService] Skipping stock deduction for Online order {order.order_number} (already handled)")
                        
                return {'status': 'success', 'message': 'Order completed successfully'}
        except Order.DoesNotExist:
            return {'status': 'error', 'message': 'Order not found or not pending'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}


    def sync_order(self, offline_uuid, transaction_data):
        """
        Processes an offline order synchronization request.
        """
        # 1. Prevent duplicates
        if Order.objects.filter(offline_uuid=offline_uuid).exists():
            return {
                'status': 'already_synced',
                'message': 'Transaction already processed'
            }

        try:
            with transaction.atomic():
                # 2. Identify Branch
                branch_id = transaction_data.get('branch_id')
                branch = get_object_or_404(Branch, pk=branch_id, tenant=self.tenant)

                # 3. Identify Customer
                customer_id = transaction_data.get('customer_id')
                customer = None
                if customer_id:
                    customer = Customer.objects.filter(id=customer_id, branch=branch).first()

                # 4. Create Order
                order_number = transaction_data.get('order_number') or generate_order_number(self.tenant)
                total_amount = transaction_data.get('total_amount', 0)
                
                # Determine status: Kiosk orders are pending until confirmed
                ordering_type = transaction_data.get('ordering_type') or 'pos'
                target_status = 'pending' if str(ordering_type).lower().strip() == 'kiosk' else 'completed'
                
                order = Order.objects.create(
                    id=offline_uuid, # Use client-generated UUID as PK
                    tenant=self.tenant,
                    branch=branch,
                    customer=customer,
                    cashier=self.user_profile,
                    subtotal=transaction_data.get('subtotal', total_amount),
                    tax_amount=transaction_data.get('tax_amount', 0),
                    total_amount=total_amount,
                    ordering_type=ordering_type,
                    payment_method=transaction_data.get('payment_method', 'cash'),
                    status=target_status,
                    offline_uuid=offline_uuid,
                    order_number=order_number
                )

                # 5. Process Items
                items = transaction_data.get('items', [])
                for item_data in items:
                    prod_id = item_data.get('product_id') or item_data.get('id')
                    if not prod_id:
                        continue
                        
                    product = Product.objects.get(id=prod_id, tenant=self.tenant)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item_data['quantity'],
                        price=item_data['price'],
                        item_number=generate_item_number(order)
                    )
                    
                    # 6. Inventory Deduction (Skip for online orders)
                    if order.status == 'completed' and order.ordering_type != 'online':
                        self._deduct_stock(product, item_data['quantity'], order, branch)

                return {
                    'status': 'success',
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'message': 'Transaction synced successfully'
                }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def create_transfer(self, transaction_data):
        """
        Processes a stock transfer request.
        """
        from branches.models import StockTransfer, StockTransferItem
        try:
            with transaction.atomic():
                source_branch_id = transaction_data.get('source_branch_id') or transaction_data.get('source_branch')
                source_branch = get_object_or_404(Branch, pk=source_branch_id, tenant=self.tenant)
                
                dest_branch_id = transaction_data.get('destination_branch_id') or transaction_data.get('destination_branch')
                dest_branch = get_object_or_404(Branch, pk=dest_branch_id, tenant=self.tenant)
                
                reference_id = transaction_data.get('reference_id') or f"TR-{uuid.uuid4().hex[:8].upper()}"
                transfer = StockTransfer.objects.create(
                    tenant=self.tenant,
                    source_branch=source_branch,
                    destination_branch=dest_branch,
                    reference_id=reference_id,
                    status='pending',
                    created_by=self.user_profile,
                    notes=transaction_data.get('notes', '')
                )
                
                items = transaction_data.get('items', [])
                for item in items:
                    product = Product.objects.get(id=item['product_id'], tenant=self.tenant)
                    StockTransferItem.objects.create(
                        transfer=transfer,
                        product=product,
                        quantity=item['quantity'],
                        transfer_price=item.get('transfer_price')
                    )
                    # Deduct stock immediately
                    self._deduct_stock(product, item['quantity'])
                    
                return {'status': 'success', 'transfer_id': str(transfer.id)}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def create_purchase_order(self, transaction_data):
        """
        Processes a purchase order synchronization request.
        """
        from branches.models import PurchaseOrder, PurchaseOrderItem
        try:
            with transaction.atomic():
                branch_id = transaction_data.get('branch_id')
                branch = get_object_or_404(Branch, pk=branch_id, tenant=self.tenant)
                
                po = PurchaseOrder.objects.create(
                    tenant=self.tenant,
                    branch=branch,
                    supplier_id=transaction_data.get('supplier_id') or transaction_data.get('supplier'),
                    reference_id=transaction_data.get('reference_id'),
                    status='ordered',
                    created_by=self.user_profile,
                    total_cost=transaction_data.get('total_cost', 0),
                    notes=transaction_data.get('notes', '')
                )
                
                items = transaction_data.get('items', [])
                for item in items:
                    product = Product.objects.get(id=item.get('product_id') or item.get('id'), tenant=self.tenant)
                    PurchaseOrderItem.objects.create(
                        po=po,
                        product=product,
                        quantity=item['quantity'],
                        unit_cost=item.get('unit_cost') or item.get('cost', 0)
                    )
                    # Note: We don't update stock for POs until they are 'received'
                    
                return {'status': 'success', 'po_id': str(po.id)}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _deduct_stock(self, product, quantity, reference_order=None, branch=None):
        """
        Internal helper for stock deduction including composite products and movement logging.
        """
        if product.is_composite:
            for component in product.components.all():
                qty_to_deduct = component.quantity * quantity
                component.component_product.stock_quantity -= qty_to_deduct
                component.component_product.save()
                
                self._log_movement(component.component_product, -qty_to_deduct, reference_order, branch)
        else:
            product.stock_quantity -= quantity
            product.save()
            self._log_movement(product, -quantity, reference_order, branch)

    def _log_movement(self, product, change, order=None, branch=None):
        """Helper to create audit trails"""
        from branches.models import StockMovement
        StockMovement.objects.create(
            tenant=self.tenant,
            branch=branch or (order.branch if order else None),
            product=product,
            quantity_change=change,
            balance_after=product.stock_quantity,
            movement_type='sale',
            reference=f"Order {order.order_number if order else 'Internal'}",
            created_by=self.user_profile
        )
