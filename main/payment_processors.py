"""
Payment Gateway Integration
Handles Stripe and PayPal payment processing
"""
import os
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Optional

class PaymentProcessor(ABC):
    """Abstract base class for payment processors"""
    
    @abstractmethod
    def process_payment(self, amount: Decimal, currency: str, metadata: Dict) -> Dict:
        """Process a payment"""
        pass
    
    @abstractmethod
    def process_refund(self, transaction_id: str, amount: Optional[Decimal] = None) -> Dict:
        """Process a refund"""
        pass
    
    @abstractmethod
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        pass


class StripeProcessor(PaymentProcessor):
    """Stripe payment processor"""
    
    def __init__(self):
        # In production, these should come from environment variables
        self.api_key = os.getenv('STRIPE_SECRET_KEY', '')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
        
        # Only import stripe if we have credentials
        if self.api_key:
            try:
                import stripe
                self.stripe = stripe
                self.stripe.api_key = self.api_key
            except ImportError:
                raise ImportError("Stripe library not installed. Run: pip install stripe")
        else:
            self.stripe = None
    
    def process_payment(self, amount: Decimal, currency: str = 'usd', metadata: Dict = None) -> Dict:
        """
        Process a payment through Stripe
        
        Args:
            amount: Amount in decimal (e.g., 10.50)
            currency: Currency code (default: 'usd')
            metadata: Additional metadata to attach to payment
        
        Returns:
            Dict with status, transaction_id, and response data
        """
        if not self.stripe:
            return {
                'status': 'failed',
                'error': 'Stripe not configured. Please set STRIPE_SECRET_KEY environment variable.'
            }
        
        try:
            # Convert amount to cents (Stripe uses smallest currency unit)
            amount_cents = int(amount * 100)
            
            # Create a PaymentIntent
            intent = self.stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True},
            )
            
            return {
                'status': 'success',
                'transaction_id': intent.id,
                'client_secret': intent.client_secret,
                'amount': amount,
                'currency': currency,
                'metadata': intent
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def process_refund(self, transaction_id: str, amount: Optional[Decimal] = None) -> Dict:
        """
        Process a refund through Stripe
        
        Args:
            transaction_id: Stripe PaymentIntent ID
            amount: Optional partial refund amount (None for full refund)
        
        Returns:
            Dict with status and refund details
        """
        if not self.stripe:
            return {
                'status': 'failed',
                'error': 'Stripe not configured'
            }
        
        try:
            refund_params = {'payment_intent': transaction_id}
            
            if amount:
                # Partial refund
                refund_params['amount'] = int(amount * 100)
            
            refund = self.stripe.Refund.create(**refund_params)
            
            return {
                'status': 'success',
                'refund_id': refund.id,
                'amount': Decimal(refund.amount) / 100,
                'metadata': refund
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify Stripe webhook signature"""
        if not self.stripe or not self.webhook_secret:
            return False
        
        try:
            self.stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return True
        except Exception:
            return False


class PayPalProcessor(PaymentProcessor):
    """PayPal payment processor"""
    
    def __init__(self):
        # In production, these should come from environment variables
        self.client_id = os.getenv('PAYPAL_CLIENT_ID', '')
        self.client_secret = os.getenv('PAYPAL_CLIENT_SECRET', '')
        self.mode = os.getenv('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'
        
        # Only import paypalrestsdk if we have credentials
        if self.client_id and self.client_secret:
            try:
                import paypalrestsdk
                self.paypal = paypalrestsdk
                self.paypal.configure({
                    'mode': self.mode,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                })
            except ImportError:
                raise ImportError("PayPal SDK not installed. Run: pip install paypalrestsdk")
        else:
            self.paypal = None
    
    def process_payment(self, amount: Decimal, currency: str = 'USD', metadata: Dict = None) -> Dict:
        """
        Process a payment through PayPal
        
        Args:
            amount: Amount in decimal
            currency: Currency code (default: 'USD')
            metadata: Additional metadata
        
        Returns:
            Dict with status and payment details
        """
        if not self.paypal:
            return {
                'status': 'failed',
                'error': 'PayPal not configured. Please set PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET.'
            }
        
        try:
            payment = self.paypal.Payment({
                'intent': 'sale',
                'payer': {'payment_method': 'paypal'},
                'transactions': [{
                    'amount': {
                        'total': str(amount),
                        'currency': currency.upper()
                    },
                    'description': metadata.get('description', 'POS Payment') if metadata else 'POS Payment'
                }],
                'redirect_urls': {
                    'return_url': metadata.get('return_url', 'http://localhost:8000/payments/success') if metadata else 'http://localhost:8000/payments/success',
                    'cancel_url': metadata.get('cancel_url', 'http://localhost:8000/payments/cancel') if metadata else 'http://localhost:8000/payments/cancel'
                }
            })
            
            if payment.create():
                return {
                    'status': 'success',
                    'transaction_id': payment.id,
                    'approval_url': next((link.href for link in payment.links if link.rel == 'approval_url'), None),
                    'metadata': payment.to_dict()
                }
            else:
                return {
                    'status': 'failed',
                    'error': payment.error
                }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def process_refund(self, transaction_id: str, amount: Optional[Decimal] = None) -> Dict:
        """
        Process a refund through PayPal
        
        Args:
            transaction_id: PayPal sale ID
            amount: Optional partial refund amount
        
        Returns:
            Dict with status and refund details
        """
        if not self.paypal:
            return {
                'status': 'failed',
                'error': 'PayPal not configured'
            }
        
        try:
            sale = self.paypal.Sale.find(transaction_id)
            
            refund_params = {}
            if amount:
                refund_params['amount'] = {
                    'total': str(amount),
                    'currency': sale.amount.currency
                }
            
            refund = sale.refund(refund_params)
            
            if refund.success():
                return {
                    'status': 'success',
                    'refund_id': refund.id,
                    'amount': Decimal(refund.amount.total) if hasattr(refund, 'amount') else amount,
                    'metadata': refund.to_dict()
                }
            else:
                return {
                    'status': 'failed',
                    'error': refund.error
                }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """
        Verify PayPal webhook signature
        Note: PayPal webhook verification is more complex and typically requires
        additional setup. This is a placeholder implementation.
        """
        # PayPal webhook verification would go here
        # Requires webhook ID and certificate validation
        return True  # Placeholder


def get_payment_processor(provider: str) -> Optional[PaymentProcessor]:
    """
    Factory function to get the appropriate payment processor
    
    Args:
        provider: Payment provider name ('stripe' or 'paypal')
    
    Returns:
        PaymentProcessor instance or None
    """
    processors = {
        'stripe': StripeProcessor,
        'paypal': PayPalProcessor,
    }
    
    processor_class = processors.get(provider.lower())
    if processor_class:
        try:
            return processor_class()
        except Exception as e:
            print(f"Error initializing {provider} processor: {e}")
            return None
    return None
