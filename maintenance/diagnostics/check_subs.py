import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Tenant
from billing.models import Subscription
from django.utils import timezone

# Get all subscriptions
subscriptions = Subscription.objects.select_related('tenant', 'plan').all()

print(f"Total subscriptions: {subscriptions.count()}\n")

for sub in subscriptions:
    print(f"Tenant: {sub.tenant.name}")
    print(f"  Status: {sub.status}")
    print(f"  Plan: {sub.plan.name if sub.plan else 'None'}")
    print(f"  Current period end: {sub.current_period_end}")
    print(f"  Now: {timezone.now()}")
    if sub.current_period_end:
        print(f"  Is future: {sub.current_period_end > timezone.now()}")
    print()
