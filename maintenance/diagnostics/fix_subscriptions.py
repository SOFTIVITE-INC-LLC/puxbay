"""
One-time script to fix existing subscriptions missing current_period_end
Run this with: python manage.py shell < fix_subscriptions.py
"""

from billing.models import Subscription
from django.utils import timezone
from datetime import timedelta

# Get all active or trialing subscriptions without current_period_end
subscriptions = Subscription.objects.filter(
    status__in=['active', 'trialing'],
    current_period_end__isnull=True
)

print(f"Found {subscriptions.count()} subscriptions to fix")

for sub in subscriptions:
    if sub.plan:
        # Calculate period end based on plan interval
        if sub.plan.interval == 'monthly':
            period_end = timezone.now() + timedelta(days=30)
        elif sub.plan.interval == '6-month':
            period_end = timezone.now() + timedelta(days=180)
        elif sub.plan.interval == 'yearly':
            period_end = timezone.now() + timedelta(days=365)
        else:
            period_end = timezone.now() + timedelta(days=30)  # Default to monthly
        
        sub.current_period_end = period_end
        sub.save()
        print(f"✓ Fixed subscription for {sub.tenant.name} - expires {period_end}")
    else:
        print(f"✗ Skipped subscription for {sub.tenant.name} - no plan assigned")

print(f"\nDone! Fixed {subscriptions.count()} subscriptions")
