import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import UserProfile, Tenant
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 70)
print("USER PROFILE ANALYSIS")
print("=" * 70)

# Get all users
users = User.objects.all()

for user in users:
    profiles = UserProfile.objects.filter(user=user).select_related('tenant')
    print(f"\nUser: {user.username} (ID: {user.id}, Superuser: {user.is_superuser})")
    print(f"  Total profiles: {profiles.count()}")
    
    for profile in profiles:
        print(f"  - Profile ID: {profile.id}")
        print(f"    Tenant: {profile.tenant.name if profile.tenant else 'None'}")
        print(f"    Tenant schema: {profile.tenant.schema_name if profile.tenant else 'N/A'}")
        
        # Check subscription
        if profile.tenant:
            try:
                sub = profile.tenant.subscription
                print(f"    Subscription: {sub.status} - {sub.plan.name if sub.plan else 'No plan'}")
            except:
                print(f"    Subscription: None")
    
    print("-" * 70)

print("\n" + "=" * 70)
print("TENANT ANALYSIS")
print("=" * 70)

tenants = Tenant.objects.all()
for tenant in tenants:
    print(f"\nTenant: {tenant.name}")
    print(f"  Schema: {tenant.schema_name}")
    print(f"  Domain: {tenant.domain_url}")
    
    # Get profiles for this tenant
    profiles = UserProfile.objects.filter(tenant=tenant).select_related('user')
    print(f"  User profiles: {profiles.count()}")
    for profile in profiles:
        print(f"    - {profile.user.username}")
    
    # Check subscription
    try:
        sub = tenant.subscription
        print(f"  Subscription: {sub.status} - {sub.plan.name if sub.plan else 'No plan'}")
    except:
        print(f"  Subscription: None")
    
    print("-" * 70)
