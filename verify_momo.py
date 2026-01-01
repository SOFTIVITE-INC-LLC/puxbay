import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from storefront.models import StorefrontSettings
from accounts.models import Tenant

def verify():
    print("Verifying Mobile Money Integration...")
    
    # Check if field exists
    if not hasattr(StorefrontSettings, 'enable_mobile_money'):
        print("FAIL: enable_mobile_money field missing in StorefrontSettings")
        return

    # Get or Create Settings for first tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("SKIP: No tenant found to test with.")
        return

    settings, created = StorefrontSettings.objects.get_or_create(tenant=tenant)
    print(f"Current enable_mobile_money: {settings.enable_mobile_money}")
    
    # Enable it
    settings.enable_mobile_money = True
    settings.save()
    print("Enabled Mobile Money for tenant.")
    
    # Verify persistence
    settings.refresh_from_db()
    if settings.enable_mobile_money:
        print("SUCCESS: Mobile Money enabled successfully.")
    else:
        print("FAIL: Could not save enable_mobile_money=True")

if __name__ == '__main__':
    verify()
