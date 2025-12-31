import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Tenant, UserProfile
from billing.models import Subscription
from billing.utils import is_subscription_active
from django.utils import timezone

print("=" * 70)
print("SUBSCRIPTION MIDDLEWARE DEBUG")
print("=" * 70)

# Get all user profiles with tenants
profiles = UserProfile.objects.select_related('tenant', 'user').filter(tenant__isnull=False)

print(f"\nTotal user profiles with tenants: {profiles.count()}\n")

for profile in profiles:
    print(f"\nUser: {profile.user.username} (ID: {profile.user.id})")
    print(f"  - Is superuser: {profile.user.is_superuser}")
    print(f"  - Profile ID: {profile.id}")
    print(f"  - Tenant: {profile.tenant.name} (ID: {profile.tenant.id})")
    
    # Check subscription
    try:
        subscription = profile.tenant.subscription
        print(f"  - Has subscription: YES")
        print(f"    - Subscription ID: {subscription.id}")
        print(f"    - Status: {subscription.status}")
        print(f"    - Plan: {subscription.plan}")
        print(f"    - Current period end: {subscription.current_period_end}")
        
        # Test is_subscription_active
        is_active = is_subscription_active(profile.tenant)
        print(f"    - is_subscription_active() result: {is_active}")
        
        # Debug the conditions
        print(f"\n    Middleware check conditions:")
        print(f"      1. User authenticated: (would be True in real request)")
        print(f"      2. User is superuser: {profile.user.is_superuser}")
        print(f"      3. Has profile: YES")
        print(f"      4. Profile has tenant: YES")
        print(f"      5. Subscription is active: {is_active}")
        
        if not is_active:
            print(f"\n    *** WOULD BE REDIRECTED TO SUBSCRIPTION REQUIRED ***")
        else:
            print(f"\n    *** SHOULD HAVE ACCESS ***")
            
    except Subscription.DoesNotExist:
        print(f"  - Has subscription: NO")
        print(f"    *** WOULD BE REDIRECTED TO SUBSCRIPTION REQUIRED ***")
    
    print("-" * 70)

print("\n" + "=" * 70)
