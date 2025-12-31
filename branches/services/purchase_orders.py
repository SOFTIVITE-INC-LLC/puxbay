import uuid as uuid_lib
import json
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from main.models import Product
from ..models import PurchaseOrder, PurchaseOrderItem, Supplier

class PurchaseOrderService:
    def __init__(self, tenant, user_profile=None):
        self.tenant = tenant
        self.user_profile = user_profile

    def create_po(self, branch, supplier_id, expected_date, items_data, notes=None, uuid=None, amount_paid=0, payment_method='cash'):
        """
        Creates a new purchase order.
        items_data format: [{'product_id': UUID, 'quantity': int, 'cost': float}]
        """
        try:
            supplier = Supplier.objects.get(id=supplier_id, tenant=self.tenant)
            
            with transaction.atomic():
                # Idempotency check with UUID if provided
                if uuid:
                    existing = PurchaseOrder.objects.filter(id=uuid, tenant=self.tenant).first()
                    if existing:
                        return {'status': 'already_synced', 'po_id': str(existing.id), 'message': 'PO already exists'}

                po = PurchaseOrder.objects.create(
                    id=uuid if uuid else uuid_lib.uuid4(),
                    tenant=self.tenant,
                    branch=branch,
                    supplier=supplier,
                    created_by=self.user_profile,
                    status='ordered',
                    expected_date=expected_date,
                    notes=notes,
                    amount_paid=amount_paid,
                    payment_method=payment_method,
                    reference_id=f"PO-{uuid_lib.uuid4().hex[:8].upper()}"
                )

                total_cost = 0
                for item in items_data:
                    product_id = item.get('product_id')
                    if not product_id: continue
                    
                    product = Product.objects.get(
                        Q(branch=branch) | Q(branch__isnull=True),
                        id=product_id, 
                        tenant=self.tenant
                    )
                    qty = int(item['quantity'])
                    # Use provided cost or fallback to product cost_price
                    cost = float(item.get('cost')) if item.get('cost') is not None else float(product.cost_price)
                    
                    PurchaseOrderItem.objects.create(
                        po=po,
                        product=product,
                        quantity=qty,
                        unit_cost=cost
                    )
                    total_cost += (cost * qty)

                po.total_cost = total_cost
                po.save()

                # Update supplier outstanding balance if credit was used or partially paid
                from decimal import Decimal
                diff = Decimal(str(total_cost)) - Decimal(str(amount_paid))
                if diff > 0:
                    supplier.outstanding_balance += diff
                    supplier.save()
                    
                    # Record credit transaction
                    from main.models import SupplierCreditTransaction
                    SupplierCreditTransaction.objects.create(
                        tenant=self.tenant,
                        supplier=supplier,
                        amount=diff,
                        transaction_type='purchase',
                        reference=f"PO #{po.reference_id}",
                        created_by=self.user_profile
                    )

                return {'status': 'success', 'po_id': str(po.id), 'reference_id': po.reference_id}
        except Supplier.DoesNotExist:
            return {'status': 'error', 'message': 'Supplier not found'}
        except Product.DoesNotExist:
            return {'status': 'error', 'message': 'One or more products not found in the specified branch'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def record_supplier_payment(self, supplier, amount, user_profile, notes="", receipt_image=None):
        """Record a payment made to a supplier against our outstanding balance"""
        from decimal import Decimal
        amount = Decimal(str(amount))
        
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
            
        with transaction.atomic():
            # Reduce balance
            supplier.outstanding_balance -= amount
            supplier.save()
            
            # Record transaction
            from main.models import SupplierCreditTransaction
            return SupplierCreditTransaction.objects.create(
                tenant=supplier.tenant,
                supplier=supplier,
                amount=-amount, # Negative for payment (reduces balance)
                transaction_type='payment',
                notes=notes,
                receipt_image=receipt_image,
                created_by=user_profile
            )

