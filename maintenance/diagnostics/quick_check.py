"""
Quick diagnostic to check current subscription status and middleware behavior
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import UserProfile, Tenant
from billing.models import Subscription
from billing.utils import is_subscription_active
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 70)
print("CURRENT SUBSCRIPTION STATUS")
print("=" * 70)

# Check all tenants with subscriptions
tenants = Tenant.objects.all()

for tenant in tenants:
    print(f"\nTenant: {tenant.name}")
    print(f"  Schema: {tenant.schema_name}")
    
    # Get subscription
    try:
        sub = tenant.subscription
        is_active = is_subscription_active(tenant)
        
        print(f"  Subscription:")
        print(f"    - Status: {sub.status}")
        print(f"    - Plan: {sub.plan.name if sub.plan else 'None'}")
        print(f"    - Period end: {sub.current_period_end}")
        print(f"    - is_subscription_active(): {is_active}")
        
        if is_active:
            print(f"  ✓ Should have dashboard access")
        else:
            print(f"  ✗ Will be redirected to subscription-required")
            
    except Subscription.DoesNotExist:
        print(f"  ✗ No subscription")
        
    # Get users for this tenant
    profiles = UserProfile.objects.filter(tenant=tenant).select_related('user')
    print(f"  Users ({profiles.count()}):")
    for profile in profiles[:3]:  # Show first 3
        print(f"    - {profile.user.username} (superuser: {profile.user.is_superuser})")
    
    print("-" * 70)

print("\n" + "=" * 70)
print("TROUBLESHOOTING TIPS")
print("=" * 70)
print("\n1. If you're being redirected to /billing/subscription-required/:")
print("   - Check that is_subscription_active() returns True above")
print("   - Ensure the middleware fix was applied (check accounts/middleware.py)")
print("   - Make sure the server was restarted after the fix")
print("\n2. If you're getting 404 errors:")
print("   - Check that you're using the correct URL")
print("   - Verify the URL pattern exists in urls.py")
print("\n3. Check the server logs for [SubscriptionMiddleware] debug messages")
print("=" * 70)
