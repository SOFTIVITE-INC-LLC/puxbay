"""
Test script to diagnose subdomain login issues
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from django.test import Client
from django_tenants.utils import get_tenant_model, get_tenant_domain_model

Tenant = get_tenant_model()
Domain = get_tenant_domain_model()

print("=" * 70)
print("SUBDOMAIN LOGIN TEST")
print("=" * 70)

# Get the Softivite tenant
try:
    domain = Domain.objects.get(domain='softiviteinc.localhost')
    tenant = domain.tenant
    
    print(f"\nTenant found: {tenant.name}")
    print(f"Schema: {tenant.schema_name}")
    print(f"Domain: {domain.domain}")
    print(f"Is primary: {domain.is_primary}")
    
    # Create a test client
    client = Client(HTTP_HOST='softiviteinc.localhost:8000')
    
    print("\n" + "-" * 70)
    print("Testing GET /login/")
    print("-" * 70)
    
    response = client.get('/login/')
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Login page loaded successfully!")
    elif response.status_code == 404:
        print("✗ 404 Not Found - URL pattern may not be configured correctly")
    elif response.status_code == 500:
        print("✗ 500 Server Error - Check server logs for details")
        if hasattr(response, 'content'):
            print(f"Error content: {response.content[:500]}")
    elif response.status_code == 302:
        print(f"→ Redirect to: {response.url}")
    else:
        print(f"Unexpected status code: {response.status_code}")
    
    print("\n" + "=" * 70)
    
except Domain.DoesNotExist:
    print("\n✗ ERROR: Domain 'softiviteinc.localhost' not found in database!")
    print("\nAvailable domains:")
    for d in Domain.objects.all():
        print(f"  - {d.domain} → {d.tenant.name}")
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 70)
