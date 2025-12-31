from django.core.management.base import BaseCommand
from accounts.models import Tenant, Domain
from django.conf import settings

class Command(BaseCommand):
    help = 'Setup the initial public tenant and domain for the Puxbay system.'

    def handle(self, *args, **options):
        # Create public tenant
        if not Tenant.objects.filter(schema_name='public').exists():
            tenant = Tenant(
                schema_name='public', 
                name='Puxbay', 
                subdomain='public',
                tenant_type='standard' # Public is usually dummy type or specific
            )
            tenant.save()
            self.stdout.write(self.style.SUCCESS(f"✓ Created public tenant '{tenant.name}'"))
            
            # Add domain
            domain = Domain()
            domain.domain = 'localhost' # Default for local dev
            domain.tenant = tenant
            domain.is_primary = True
            domain.save()
            self.stdout.write(self.style.SUCCESS(f"✓ Created public domain '{domain.domain}'"))
            
            self.stdout.write(self.style.SUCCESS("\nPublic tenant setup complete! You can now access the landing page."))
        else:
            self.stdout.write(self.style.NOTICE("Public tenant already exists."))
