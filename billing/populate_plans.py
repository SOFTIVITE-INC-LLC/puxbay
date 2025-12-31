
import os
import django
import sys

# Setup settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from billing.models import Plan

def populate():
    # 1. Starter
    plan, created = Plan.objects.update_or_create(
        name="Starter",
        defaults={
            "description": "Perfect for small shops and startups getting off the ground.",
            "price": 29.00,
            "max_branches": 1,
            "max_users": 3,
            "api_access": False,
            "api_daily_limit": 0,
            "features": {
                "branches": "1 Branch Location",
                "staff": "Up to 3 Staff Members",
                "reporting": "Basic Reporting",
                "support": "Email Support"
            },
            "is_active": True
        }
    )
    print(f"{'Created' if created else 'Updated'} Starter plan.")

    # 2. Growth
    plan, created = Plan.objects.update_or_create(
        name="Growth",
        defaults={
            "description": "For growing businesses that need more power and locations.",
            "price": 79.00,
            "max_branches": 5,
            "max_users": 100, # Unlimited effectively
            "api_access": True,
            "api_daily_limit": 1000,
            "features": {
                "branches": "Up to 5 Branch Locations",
                "staff": "Unlimited Staff Members",
                "analytics": "Advanced Analytics & Exports",
                "support": "Priority 24/7 Support",
                "offline": "Offline Sync Priority"
            },
            "is_active": True
        }
    )
    print(f"{'Created' if created else 'Updated'} Growth plan.")

    # 3. Enterprise
    plan, created = Plan.objects.update_or_create(
        name="Enterprise",
        defaults={
            "description": "Maximum power and control for large organizations.",
            "price": 199.00,
            "max_branches": 1000,
            "max_users": 1000,
            "api_access": True,
            "api_daily_limit": 50000,
            "features": {
                "branches": "Unlimited Branches",
                "manager": "Dedicated Success Manager",
                "api": "Custom Integrations (API)",
                "sla": "SLA & Contract billing"
            },
            "is_active": True
        }
    )
    print(f"{'Created' if created else 'Updated'} Enterprise plan.")

    # 4. Developer
    plan, created = Plan.objects.update_or_create(
        name="Developer",
        defaults={
            "description": "Build custom solutions and integrations on our platform.",
            "price": 49.00,
            "max_branches": 1,
            "max_users": 1,
            "api_access": True,
            "api_daily_limit": 5000,
            "features": {
                "api": "Full API Access (5k req/day)",
                "dev": "Developer Tools & SDK",
                "sandbox": "Sandbox Environment",
                "support": "Technical Discord Support"
            },
            "is_active": True
        }
    )
    print(f"{'Created' if created else 'Updated'} Developer plan.")

if __name__ == "__main__":
    populate()
