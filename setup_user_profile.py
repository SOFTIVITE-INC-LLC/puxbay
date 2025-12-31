import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Tenant, Branch, UserProfile

# Check existing users and profiles
print("Users and Profiles:")
print("=" * 60)

for user in User.objects.all():
    print(f"\nUser: {user.username}")
    profiles = UserProfile.objects.filter(user=user)
    for profile in profiles:
        print(f"  - Tenant: {profile.tenant.name}, Branch: {profile.branch.name if profile.branch else 'None'}, Role: {profile.role}")

# Create a profile for admin on eduxkope if needed
tenant = Tenant.objects.get(schema_name='eduxkope')
user = User.objects.get(username='admin')
branch = Branch.objects.filter(tenant=tenant).first()

profile, created = UserProfile.objects.get_or_create(
    user=user,
    tenant=tenant,
    defaults={
        'branch': branch,
        'role': 'admin',
        'is_email_verified': True
    }
)

if created:
    print(f"\n✓ Created profile for {user.username} on {tenant.name}")
else:
    print(f"\n✓ Profile already exists for {user.username} on {tenant.name}")
