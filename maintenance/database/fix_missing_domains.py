import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Tenant, Domain

def fix_domains(base_domain='localhost'):
    print(f"Fixing domains using base: {base_domain} ...")
    tenants = Tenant.objects.all()
    count = 0
    for tenant in tenants:
        if tenant.schema_name == 'public':
            continue
            
        # Check if domain exists
        if not Domain.objects.filter(tenant=tenant).exists():
            full_domain = f"{tenant.subdomain}.{base_domain}"
            Domain.objects.create(
                domain=full_domain,
                tenant=tenant,
                is_primary=True
            )
            print(f"Created domain '{full_domain}' for tenant '{tenant.name}'")
            count += 1
        else:
            print(f"Tenant '{tenant.name}' already has a domain.")
            
    print(f"Finished. Fixed {count} tenants.")

if __name__ == '__main__':
    fix_domains()
