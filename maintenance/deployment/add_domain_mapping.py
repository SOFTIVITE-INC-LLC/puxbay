#!/usr/bin/env python
"""
Add domain mapping for puxbay.com to the public tenant.
Run this script to fix the "No tenant for hostname" error.
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/opt/puxbay')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Tenant, Domain

def add_domain_mapping():
    """Add puxbay.com domain to public tenant"""
    
    # Get or create public tenant
    public_tenant, created = Tenant.objects.get_or_create(
        schema_name='public',
        defaults={
            'name': 'Puxbay',
            'subdomain': 'public',
            'tenant_type': 'standard'
        }
    )
    
    if created:
        print(f"✓ Created public tenant: {public_tenant.name}")
    else:
        print(f"✓ Found existing public tenant: {public_tenant.name}")
    
    # Add domain mappings
    domains_to_add = [
        'puxbay.com',
        'www.puxbay.com',
        'localhost',
        '127.0.0.1',
    ]
    
    for domain_name in domains_to_add:
        domain, created = Domain.objects.get_or_create(
            domain=domain_name,
            defaults={
                'tenant': public_tenant,
                'is_primary': (domain_name == 'puxbay.com')
            }
        )
        
        if created:
            print(f"✓ Added domain: {domain_name}")
        else:
            print(f"  Domain already exists: {domain_name}")
    
    print("\n✓ Domain mapping complete!")
    print(f"\nYou can now access the site at:")
    for domain_name in domains_to_add:
        print(f"  - https://{domain_name}")

if __name__ == '__main__':
    try:
        add_domain_mapping()
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
