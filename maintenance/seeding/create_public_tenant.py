from accounts.models import Tenant, Domain

# Create public tenant
if not Tenant.objects.filter(schema_name='public').exists():
    tenant = Tenant(schema_name='public', name='Puxbay', subdomain='public')
    tenant.save()
    
    # Add domain
    domain = Domain()
    domain.domain = 'localhost' # or your domain
    domain.tenant = tenant
    domain.is_primary = True
    domain.save()
    print("Public tenant created successfully.")
else:
    print("Public tenant already exists.")
