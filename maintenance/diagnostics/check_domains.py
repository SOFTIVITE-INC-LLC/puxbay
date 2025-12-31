import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from django_tenants.utils import get_tenant_model, get_tenant_domain_model

Tenant = get_tenant_model()
Domain = get_tenant_domain_model()

print("=" * 70)
print("TENANT AND DOMAIN CONFIGURATION")
print("=" * 70)

# Get all tenants
tenants = Tenant.objects.all()
print(f"\nTotal tenants: {tenants.count()}\n")

for tenant in tenants:
    print(f"Tenant: {tenant.name}")
    print(f"  Schema: {tenant.schema_name}")
    
    # Get all domains for this tenant
    domains = Domain.objects.filter(tenant=tenant)
    print(f"  Domains ({domains.count()}):")
    for domain in domains:
        print(f"    - {domain.domain} (Primary: {domain.is_primary})")
    
    print("-" * 70)

print("\n" + "=" * 70)
print("SUBDOMAIN ACCESS GUIDE")
print("=" * 70)
print("\nTo access a tenant via subdomain:")
print("1. Find the domain entry for the tenant above")
print("2. Use that exact domain in your browser")
print("\nExamples:")
print("  - If domain is 'softiviteinc.localhost', use: http://softiviteinc.localhost:8000/login/")
print("  - If domain is 'softivite.localhost', use: http://softivite.localhost:8000/login/")
print("\nNote: The subdomain must EXACTLY match the domain field!")
print("=" * 70)
