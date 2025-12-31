from django.core.management.base import BaseCommand
from accounts.models import SEOSettings, Tenant
from django.core.files.base import ContentFile
import requests

class Command(BaseCommand):
    help = 'Seeds global SEO settings for the public tenant'

    def handle(self, *args, **options):
        self.stdout.write('Seeding SEO Settings for Public Tenant...')

        try:
            public_tenant = Tenant.objects.get(schema_name='public')
        except Tenant.DoesNotExist:
            self.stdout.write(self.style.ERROR('Public tenant not found. Please ensure your multi-tenant setup is complete.'))
            return

        seo, created = SEOSettings.objects.update_or_create(
            tenant=public_tenant,
            defaults={
                'meta_title': 'Puxbay - The Ultimate All-in-One Cloud POS & ERP',
                'meta_description': 'Empower your retail business with Puxbay. Manage Point of Sale, Inventory, CRM, and E-commerce from one unified dashboard. Free trial available!',
                'keywords': 'cloud pos, erp software, inventory management, retail pos, ghana pos, omnichannel retail, puxbay',
                'og_title': 'Puxbay | Next-Gen Retail Management Software',
                'og_description': 'The most comprehensive retail platform in Africa. Sell online, offline, and via self-service kiosks with Puxbay.',
                'contact_email': 'hello@puxbay.com',
                'support_email': 'support@puxbay.com',
                'contact_phone': '+233 (0) 24 000 0000',
                'contact_address': 'Silver Star Tower, Airport City, Accra, Ghana',
                'office_hours': 'Mon-Sat 8am-6pm GMT',
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created SEO settings for {public_tenant.name}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated SEO settings for {public_tenant.name}"))

        self.stdout.write(self.style.SUCCESS('SEO Seeding completed.'))
