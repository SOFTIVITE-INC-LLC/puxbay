import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from billing.models import PricingPlan, PlanFeature, Plan

def populate():
    # Clear existing
    PricingPlan.objects.all().delete()
    PlanFeature.objects.all().delete()
    Plan.objects.all().delete()
    print("Cleared existing pricing plans and billing plans.")

    # 1. Starter
    starter = PricingPlan.objects.create(
        name="Starter",
        slug="starter",
        price_monthly=29.00,
        price_yearly=290.00,
        currency="$",
        description="Perfect for small shops and startups getting off the ground.",
        is_popular=False,
        button_text="Start 14-day trial",
        order=1
    )
    PlanFeature.objects.create(plan=starter, text="1 Branch Location", is_available=True, order=1)
    PlanFeature.objects.create(plan=starter, text="Up to 3 Staff Members", is_available=True, order=2)
    PlanFeature.objects.create(plan=starter, text="Basic Reporting", is_available=True, order=3)
    PlanFeature.objects.create(plan=starter, text="Email Support", is_available=True, order=4)
    print("Created Starter plan.")

    # 2. Growth
    growth = PricingPlan.objects.create(
        name="Growth",
        slug="growth",
        price_monthly=79.00,
        price_yearly=790.00,
        currency="$",
        description="For growing businesses that need more power and locations.",
        is_popular=True,
        button_text="Get Started",
        order=2
    )
    PlanFeature.objects.create(plan=growth, text="Up to 5 Branch Locations", is_available=True, order=1)
    PlanFeature.objects.create(plan=growth, text="Unlimited Staff Members", is_available=True, order=2)
    PlanFeature.objects.create(plan=growth, text="Advanced Analytics & Exports", is_available=True, order=3)
    PlanFeature.objects.create(plan=growth, text="Priority 24/7 Support", is_available=True, order=4)
    PlanFeature.objects.create(plan=growth, text="Offline Sync Priority", is_available=True, order=5)
    print("Created Growth plan.")

    # 3. Enterprise
    enterprise = PricingPlan.objects.create(
        name="Enterprise",
        slug="enterprise",
        price_monthly=199.00,
        price_yearly=1990.00,
        currency="$",
        description="Maximum power and control for large organizations.",
        is_popular=False,
        button_text="Contact Sales",
        order=3
    )
    PlanFeature.objects.create(plan=enterprise, text="Unlimited Branches", is_available=True, order=1)
    PlanFeature.objects.create(plan=enterprise, text="Dedicated Success Manager", is_available=True, order=2)
    PlanFeature.objects.create(plan=enterprise, text="Custom Integrations (API)", is_available=True, order=3)
    PlanFeature.objects.create(plan=enterprise, text="SLA & Contract billing", is_available=True, order=4)
    PlanFeature.objects.create(plan=enterprise, text="SLA & Contract billing", is_available=True, order=4)
    print("Created Enterprise plan.")

    # --- Billing Plans (for Subscription model) ---
    
    # Starter
    Plan.objects.create(name="Starter Monthly", price=29.00, interval='monthly', max_branches=1, max_users=3)
    Plan.objects.create(name="Starter Yearly", price=290.00, interval='yearly', max_branches=1, max_users=3)

    # Growth
    Plan.objects.create(name="Growth Monthly", price=79.00, interval='monthly', max_branches=5, max_users=100)
    Plan.objects.create(name="Growth Yearly", price=790.00, interval='yearly', max_branches=5, max_users=100)

    # Enterprise
    Plan.objects.create(name="Enterprise Monthly", price=199.00, interval='monthly', max_branches=1000, max_users=1000)
    Plan.objects.create(name="Enterprise Yearly", price=1990.00, interval='yearly', max_branches=1000, max_users=1000)

    # Developer Plans (Grant API access by default)
    Plan.objects.create(
        name="Developer Monthly", 
        price=49.00, 
        interval='monthly', 
        max_branches=5, 
        max_users=10, 
        is_developer_only=True
    )
    Plan.objects.create(
        name="Developer Yearly", 
        price=490.00, 
        interval='yearly', 
        max_branches=5, 
        max_users=10, 
        is_developer_only=True
    )

    print("Created Billing Plans (including Developer tiers).")

populate()
