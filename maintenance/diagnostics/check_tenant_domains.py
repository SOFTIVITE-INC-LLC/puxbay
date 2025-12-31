import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Tenant

print("=" * 70)
print("TENANT SUBDOMAIN CHECK")
print("=" * 70)

tenants = Tenant.objects.all()

print(f"\nTotal tenants: {tenants.count()}\n")

for tenant in tenants:
    print(f"Tenant: {tenant.name}")
    print(f"  Schema name: {tenant.schema_name}")
    print(f"  Domain URL: {tenant.domain_url}")
    
    # Check if this matches the subdomain you're trying to access
    if 'softivite' in tenant.name.lower() or 'softivite' in tenant.schema_name.lower():
        print(f"  *** This might be the tenant you're trying to access ***")
    
    print("-" * 70)

print("\n" + "=" * 70)
print("EXPECTED SUBDOMAIN FORMAT")
print("=" * 70)
print("\nFor django-tenants, the subdomain should match the 'domain_url' field.")
print("If domain_url is 'softiviteinc.localhost', access via:")
print("  http://softiviteinc.localhost:8000/")
print("\nIf domain_url is 'softiviteinc', access via:")
print("  http://softiviteinc.localhost:8000/")
print("=" * 70)
