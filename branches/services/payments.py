import json
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from main.models import (
    Product, Customer, Order, OrderItem, 
    GiftCard, StoreCreditTransaction, 
    LoyaltyTransaction, CRMSettings,
    Payment, PaymentMethod,
    CustomerCreditTransaction
)

class PaymentService:
    def __init__(self, user, branch, data):
        self.user = user
        self.branch = branch
        self.data = data
        self.tenant = user.profile.tenant

    def process_checkout(self):
        items = self.data.get('items', [])
        customer_id = self.data.get('customer_id')
        
        # New split payment format: {'payments': [{'method': 'cash', 'amount': 10}, ...]}
        payments_data = self.data.get('payments', [])
        
        # Fallback for old single-payment format
        if not payments_data:
            payments_data = [{
                'method': self.data.get('payment_method', 'cash'),
                'amount': None, # To be calculated from total if only one payment
                'gift_card_code': self.data.get('gift_card_code'),
                'payment_ref': self.data.get('payment_ref')
            }]

        if not items:
            return {'success': False, 'error': 'Cart is empty'}

        try:
            with transaction.atomic():
                # 1. Determine Customer
                customer = None
                is_wholesale = False
                if customer_id:
                    customer = Customer.objects.filter(pk=customer_id, tenant=self.tenant).first()
                    if customer and customer.customer_type == 'wholesale':
                        is_wholesale = True

                # 2. Calculate Total and Validate Stock
                total_amount = Decimal('0.00')
                validated_items = []
                
                for item in items:
                    if item.get('type') == 'gift_card':
                        # Handle selling a new Gift Card
                        item_price = Decimal(str(item.get('price', 0)))
                        total_amount += item_price
                        validated_items.append({
                            'type': 'gift_card',
                            'product': None,
                            'qty': 1,
                            'price': item_price,
                            'gc_code': item.get('gc_code')
                        })
                        continue

                    product = Product.objects.get(pk=item['id'], branch=self.branch)
                    qty = int(item['quantity'])
                    
                    if product.stock_quantity < qty:
                        raise Exception(f'Not enough stock for {product.name}')
                    
                    price_to_charge = product.price
                    if is_wholesale and product.wholesale_price > 0:
                        price_to_charge = product.wholesale_price
                    
                    total_amount += (price_to_charge * qty)
                    validated_items.append({
                        'type': 'product',
                        'product': product,
                        'qty': qty,
                        'price': price_to_charge
                    })

                # 3. Validate Payments and Balances
                total_paid = Decimal('0.00')
                valid_payments = []
                
                # If only one payment and no amount specified, it's the full total
                if len(payments_data) == 1 and payments_data[0].get('amount') is None:
                    payments_data[0]['amount'] = total_amount

                for p_data in payments_data:
                    method = p_data.get('method')
                    p_amount = Decimal(str(p_data.get('amount', 0)))
                    total_paid += p_amount
                    
                    p_info = {
                        'method': method,
                        'amount': p_amount,
                        'ref': p_data.get('payment_ref')
                    }
                    
                    if method == 'gift_card':
                        code = p_data.get('gift_card_code')
                        if not code:
                            return {'success': False, 'error': 'Gift Card code required'}
                        try:
                            gift_card = GiftCard.objects.get(code=code, tenant=self.tenant)
                            if gift_card.status != 'active':
                                return {'success': False, 'error': f'Gift Card {code} is not active'}
                            if gift_card.expiry_date and gift_card.expiry_date < timezone.now().date():
                                return {'success': False, 'error': f'Gift Card {code} has expired'}
                            if gift_card.balance < p_amount:
                                return {'success': False, 'error': f'Insufficient Gift Card balance for {code}. Balance: {gift_card.balance}'}
                            p_info['gift_card'] = gift_card
                        except GiftCard.DoesNotExist:
                            return {'success': False, 'error': f'Invalid Gift Card code: {code}'}
                    
                    elif method == 'store_credit':
                        if not customer:
                            return {'success': False, 'error': 'Customer required for Store Credit'}
                        if customer.store_credit_balance < p_amount:
                            return {'success': False, 'error': f'Insufficient Store Credit. Balance: {customer.store_credit_balance}'}
                    
                    elif method == 'loyalty_points':
                        if not customer:
                            return {'success': False, 'error': 'Customer required for Loyalty Points'}
                        
                        settings, _ = CRMSettings.objects.get_or_create(tenant=self.tenant)
                        if settings.redemption_rate <= 0:
                            return {'success': False, 'error': 'System error: Redemption rate is not configured correctly'}
                        
                        required_points = p_amount / settings.redemption_rate
                        if customer.loyalty_points < required_points:
                            return {'success': False, 'error': f'Insufficient Loyalty Points. Balance: {customer.loyalty_points}, Required: {required_points:.0f}'}
                        p_info['loyalty_points_to_redeem'] = required_points
                    
                    elif method == 'credit':
                        if not customer:
                            return {'success': False, 'error': 'Customer required for Credit Purchase'}
                        
                        # Check permission for salesmen
                        is_privileged = self.user_profile.role in ['admin', 'manager']
                        if not is_privileged and not self.user_profile.can_perform_credit_sales:
                            return {'success': False, 'error': 'You do not have permission to perform credit transactions.'}
                        
                        potential_debt = customer.outstanding_debt + p_amount
                        if customer.credit_limit > 0 and potential_debt > customer.credit_limit:
                            return {'success': False, 'error': f'Credit limit exceeded. Limit: {customer.credit_limit}, New Debt: {potential_debt}'}
                        if customer.credit_limit <= 0 and p_amount > 0:
                            return {'success': False, 'error': 'Customer does not have a credit facility enabled.'}

                    valid_payments.append(p_info)

                if total_paid < total_amount:
                    return {'success': False, 'error': f'Insufficient payment. Paid: {total_paid}, Required: {total_amount}'}

                # 4. Create Order
                from utils.identifier_generator import generate_order_number, generate_item_number
                order_number = generate_order_number(self.tenant)
                
                # Determine order-level payment method (mark as split if multiple)
                order_method = 'split' if len(valid_payments) > 1 else valid_payments[0]['method']

                order = Order.objects.create(
                    tenant=self.tenant,
                    branch=self.branch,
                    cashier=self.user.profile,
                    customer=customer,
                    order_number=order_number,
                    total_amount=total_amount,
                    amount_paid=total_paid,
                    status='completed',
                    payment_method=order_method,
                    payment_reference=valid_payments[0]['ref'] if valid_payments else None
                )

                # 5. Create Order Items and Deduct Stock / Issue Gift Cards
                for item in validated_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        item_number=generate_item_number(order),
                        quantity=item['qty'],
                        price=item['price']
                    )
                    
                    if item['type'] == 'gift_card':
                        # Automatically create and activate the gift card
                        import uuid
                        gc_code = item['gc_code'] or f"GC-{uuid.uuid4().hex[:8].upper()}"
                        GiftCard.objects.create(
                            tenant=self.tenant,
                            code=gc_code,
                            balance=item['price'],
                            status='active',
                            customer=customer # Assign to customer if known
                        )
                    else:
                        # Deduct Stock
                        item['product'].stock_quantity -= item['qty']
                        item['product'].save()

                # 6. Finalize Payment Deductions and Create Payment Records
                for p in valid_payments:
                    method = p['method']
                    amount = p['amount']
                    
                    # Create Payment record for split tracing
                    Payment.objects.create(
                        tenant=self.tenant,
                        order=order,
                        # We try to match with a PaymentMethod object if possible, 
                        # but for simple Cash/GiftCard we might not have a formal provider record.
                        # For now, we'll need to handle this carefully.
                        # Maybe we shouldn't enforce PaymentMethod FK if it's not a gateway.
                        # But the model says it's required.
                        # Let's find or create a default PaymentMethod for 'cash', 'gift_card', etc.
                        payment_method=self._get_or_create_payment_method(method),
                        amount=amount,
                        status='completed',
                        transaction_id=p['ref']
                    )

                    if method == 'gift_card':
                        gc = p['gift_card']
                        gc.balance -= amount
                        gc.save()

                    elif method == 'store_credit':
                        customer.store_credit_balance -= amount
                        customer.save()
                        StoreCreditTransaction.objects.create(
                            tenant=self.tenant,
                            customer=customer,
                            amount=-amount,
                            reference=f"Order Payment #{order.order_number}"
                        )

                    elif method == 'loyalty_points':
                        points_to_redeem = p['loyalty_points_to_redeem']
                        customer.loyalty_points -= points_to_redeem
                        customer.save()
                        LoyaltyTransaction.objects.create(
                            tenant=self.tenant,
                            customer=customer,
                            order=order,
                            points=-points_to_redeem,
                            transaction_type='redeem',
                            description=f"Redeemed for Order #{order.order_number}"
                        )

                    elif method == 'credit':
                        customer.outstanding_debt += amount
                        customer.save()
                        CustomerCreditTransaction.objects.create(
                            tenant=self.tenant,
                            customer=customer,
                            amount=amount,
                            transaction_type='purchase',
                            reference=f"Order #{order.order_number}",
                            created_by=self.user.profile
                        )

                # 7. CRM: Loyalty Points & Tier Upgrades (only for non-points portions?)
                # Usually points are earned on the total value of the order, 
                # but some businesses only award points on the portion NOT paid by points.
                # Here we'll award on the total_amount for simplicity, same as before.
                if customer:
                    customer.total_spend += total_amount
                    customer.total_orders += 1
                    customer.last_purchase_at = timezone.now()
                    
                    is_first_purchase = (customer.total_orders == 1)
                    
                    # Loyalty Points Earning
                    settings, _ = CRMSettings.objects.get_or_create(tenant=self.tenant)
                    points_earned = total_amount * settings.points_per_currency
                    
                    if points_earned > 0:
                        customer.loyalty_points += points_earned
                        LoyaltyTransaction.objects.create(
                            tenant=self.tenant,
                            customer=customer,
                            order=order,
                            points=points_earned,
                            transaction_type='earn',
                            description=f"Earned from Order #{order.order_number}"
                        )
                    
                    tier_changed = customer.calculate_tier()
                    customer.save()

                    # Trigger Marketing Automation
                    from main.services.marketing_service import trigger_automated_campaigns
                    if is_first_purchase:
                        trigger_automated_campaigns('first_purchase', customer)
                    if tier_changed:
                        trigger_automated_campaigns('tier_up', customer)

                # 8. Workforce: Evaluate Achievements
                from branches.services.gamification_service import GamificationService
                gamification = GamificationService(tenant=self.tenant)
                gamification.evaluate_achievements(self.user.profile)

                return {'success': True, 'order_id': order.id}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _get_or_create_payment_method(self, method_name):
        """Helper to get a PaymentMethod object for the given name/provider"""
        # Map simple POS methods to providers
        provider_map = {
            'cash': 'cash',
            'card': 'card',
            'mobile': 'mobile',
            'gift_card': 'cash', # Treat as internal cash-like for now or add 'gift_card' to choices
            'store_credit': 'cash',
            'loyalty_points': 'cash',
            'credit': 'bank', # Associate with accounts receivable/payable
            'stripe': 'stripe',
            'paystack': 'card', # Usually card
        }
        
        provider = provider_map.get(method_name, 'cash')
        
        pm, _ = PaymentMethod.objects.get_or_create(
            tenant=self.tenant,
            name=method_name.capitalize(),
            defaults={'provider': provider, 'is_active': True}
        )
        return pm

    @staticmethod
    def record_customer_payment(customer, amount, user, notes=""):
        """Record a payment received from a customer against their debt"""
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
            
        with transaction.atomic():
            # Reduce debt
            customer.outstanding_debt -= amount
            customer.save()
            
            # Record transaction
            from main.models import CustomerCreditTransaction
            return CustomerCreditTransaction.objects.create(
                tenant=customer.tenant,
                customer=customer,
                amount=-amount, # Negative for payment (reduces debt)
                transaction_type='payment',
                notes=notes,
                created_by=user.profile
            )

