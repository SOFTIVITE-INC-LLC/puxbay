import os
import django

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from billing.models import PaymentGatewayConfig

def populate_gateways():
    gateways = [
        {'name': 'Stripe', 'slug': 'stripe', 'description': 'Credit Card, Apple Pay'},
        {'name': 'Paystack', 'slug': 'paystack', 'description': 'Card, Bank, MoMo'},
        {'name': 'PayPal', 'slug': 'paypal', 'description': 'Fast, Simple, Secure'},
        # Optional: Add Cash if requested later, but user specified these 3.
    ]

    print("Populating Subscription Payment Gateways...")
    created_count = 0
    updated_count = 0

    for gw in gateways:
        obj, created = PaymentGatewayConfig.objects.update_or_create(
            slug=gw['slug'],
            defaults=gw
        )
        if created:
            print(f"Created: {gw['name']}")
            created_count += 1
        else:
            print(f"Updated: {gw['name']}")
            updated_count += 1

    print(f"Summary: {created_count} Created, {updated_count} Updated.")

if __name__ == "__main__":
    populate_gateways()
