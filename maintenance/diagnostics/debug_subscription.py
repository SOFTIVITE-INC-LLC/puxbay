import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Tenant
from billing.models import Subscription
from billing.utils import is_subscription_active, get_tenant_subscription
from django.utils import timezone

output_file = "subscription_debug_output.txt"

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("=" * 60 + "\n")
    f.write("SUBSCRIPTION DEBUG\n")
    f.write("=" * 60 + "\n")
    
    tenants = Tenant.objects.all()
    f.write(f"\nTotal tenants: {tenants.count()}\n\n")
    
    for tenant in tenants:
        f.write(f"\nTenant: {tenant.name} (ID: {tenant.id})\n")
        f.write("-" * 60 + "\n")
        
        # Check if subscription exists
        try:
            subscription = tenant.subscription
            f.write(f"[OK] Has subscription relationship\n")
            f.write(f"  - Subscription ID: {subscription.id}\n")
            f.write(f"  - Status: {subscription.status}\n")
            f.write(f"  - Plan: {subscription.plan}\n")
            f.write(f"  - Current period end: {subscription.current_period_end}\n")
            f.write(f"  - Now: {timezone.now()}\n")
            
            if subscription.current_period_end:
                is_future = subscription.current_period_end > timezone.now()
                f.write(f"  - Period end is in future: {is_future}\n")
            
            # Test the utility function
            is_active = is_subscription_active(tenant)
            f.write(f"  - is_subscription_active() result: {is_active}\n")
            
            # Debug the logic
            f.write(f"\n  Debug checks:\n")
            f.write(f"    - Status in ['active', 'trialing']: {subscription.status in ['active', 'trialing']}\n")
            f.write(f"    - Has plan: {subscription.plan is not None}\n")
            if subscription.current_period_end:
                f.write(f"    - Period end > now: {subscription.current_period_end > timezone.now()}\n")
            
        except Subscription.DoesNotExist:
            f.write(f"[ERROR] No subscription found\n")
            is_active = is_subscription_active(tenant)
            f.write(f"  - is_subscription_active() result: {is_active}\n")
    
    f.write("\n" + "=" * 60 + "\n")

print(f"Debug output written to {output_file}")
