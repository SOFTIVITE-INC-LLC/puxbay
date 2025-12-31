import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from accounts.models import UserProfile, Tenant
from billing.models import Subscription
from billing.utils import is_subscription_active

User = get_user_model()

print("=" * 70)
print("SUBSCRIPTION ACCESS TEST")
print("=" * 70)

# Get a user with a tenant and subscription
profiles = UserProfile.objects.select_related('user', 'tenant').filter(
    tenant__isnull=False
)

for profile in profiles:
    user = profile.user
    tenant = profile.tenant
    
    print(f"\nUser: {user.username}")
    print(f"Tenant: {tenant.name} ({tenant.schema_name})")
    print(f"Domain: {tenant.domain_url}")
    
    # Check subscription
    try:
        sub = tenant.subscription
        print(f"Subscription Status: {sub.status}")
        print(f"Plan: {sub.plan.name if sub.plan else 'None'}")
        print(f"Current period end: {sub.current_period_end}")
        is_active = is_subscription_active(tenant)
        print(f"Is Active: {is_active}")
        
        if is_active:
            print("\n✓ This user SHOULD have access to the dashboard")
        else:
            print("\n✗ This user should be redirected to subscription-required")
            
    except Subscription.DoesNotExist:
        print("Subscription: None")
        print("\n✗ This user should be redirected to subscription-required")
    
    print("-" * 70)

print("\n" + "=" * 70)
print("RECOMMENDATION")
print("=" * 70)
print("\nThe fix has been applied to accounts/middleware.py")
print("The server needs to be restarted for changes to take effect.")
print("\nPlease:")
print("1. Restart the Django development server")
print("2. Try accessing the dashboard again")
print("3. Check if the redirect issue is resolved")
print("=" * 70)
