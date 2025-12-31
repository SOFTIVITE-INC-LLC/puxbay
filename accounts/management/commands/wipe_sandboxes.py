from django.core.management.base import BaseCommand
from django.utils import timezone
from django_tenants.utils import schema_context
from accounts.models import Tenant

class Command(BaseCommand):
    help = 'Wipes/Deletes expired sandbox tenants and their schemas'

    def handle(self, *args, **options):
        now = timezone.now()
        expired_sandboxes = Tenant.objects.filter(
            is_sandbox=True,
            sandbox_wipe_at__lte=now
        )

        count = expired_sandboxes.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No expired sandboxes found.'))
            return

        self.stdout.write(f'Found {count} expired sandboxes. Starting cleanup...')

        for sandbox in expired_sandboxes:
            name = sandbox.name
            subdomain = sandbox.subdomain
            
            try:
                # With django-tenants, deleting the tenant model also drops the schema
                # if auto_drop_schema is True (defaults to True if not specified)
                sandbox.delete()
                self.stdout.write(self.style.SUCCESS(f'Successfully deleted sandbox: {name} ({subdomain})'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to delete sandbox {name}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'Cleanup complete. Deleted {count} sandboxes.'))
