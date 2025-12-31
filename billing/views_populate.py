from django.http import HttpResponse
from billing.models import Plan, PaymentGatewayConfig

def populate_plans_view(request):
    base_plans = [
        {
            'name': 'Starter',
            'base_price': 29.99,
            'description': 'Perfect for small businesses just getting started.',
            'max_branches': 1,
            'max_users': 5,
            'features': {'custom_domain': False, 'analytics': 'basic', 'support': 'email'},
            'is_developer_only': False
        },
        {
            'name': 'Professional',
            'base_price': 79.99,
            'description': 'Ideal for growing businesses with multiple locations.',
            'max_branches': 5,
            'max_users': 20,
            'features': {'custom_domain': True, 'analytics': 'advanced', 'support': 'priority'},
            'is_developer_only': False
        },
        {
            'name': 'Enterprise',
            'base_price': 199.99,
            'description': 'For large organizations requiring maximum flexibility.',
            'max_branches': 20,
            'max_users': 100,
            'features': {'custom_domain': True, 'analytics': 'full', 'support': '24/7'},
            'is_developer_only': False
        },
    ]

    intervals = [
        ('monthly', 1.0, 0),        # 1x price
        ('6-month', 5.1, 15),     # ~15% off (5.1 months price instead of 6)
        ('yearly', 9.0, 25),      # 25% off (9 months price instead of 12)
    ]

    # Regional pricing baseline (e.g., 1 USD = 15 GHS)
    ghs_rate = 15.0

    created_count = 0
    updated_count = 0
    
    for base in base_plans:
        for interval_code, price_multiplier, discount_pct in intervals:
            usd_price = float(base['base_price']) * price_multiplier
            ghs_price = usd_price * ghs_rate
            
            plan_data = {
                'name': base['name'],
                'price': round(usd_price, 2),
                'price_ghs': round(ghs_price, 2),
                'interval': interval_code,
                'description': base['description'],
                'max_branches': base['max_branches'],
                'max_users': base['max_users'],
                'features': base['features'],
                'is_developer_only': base['is_developer_only'],
                'is_active': True
            }

            plan, created = Plan.objects.update_or_create(
                name=plan_data['name'],
                interval=plan_data['interval'],
                defaults=plan_data
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1

    # Populate Payment Gateways
    gateways = [
        {'name': 'Stripe', 'slug': 'stripe', 'description': 'Credit Card, Apple Pay'},
        {'name': 'Paystack', 'slug': 'paystack', 'description': 'Card, Bank, MoMo'},
        {'name': 'PayPal', 'slug': 'paypal', 'description': 'Fast, Simple, Secure'},
    ]
    for gw in gateways:
        PaymentGatewayConfig.objects.get_or_create(
            slug=gw['slug'],
            defaults=gw
        )

    return HttpResponse(f"Successfully processed {created_count + updated_count} plans ({created_count} created, {updated_count} updated) and initialized {len(gateways)} gateways.")
