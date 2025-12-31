from celery import shared_task
import time
from django.core.mail import send_mail

@shared_task
def debug_background_task(arg):
    print(f'Background task received: {arg}')
    time.sleep(2)
    return f'Processed {arg}'

@shared_task
def sync_global_prices_task(tenant_id, sku, new_price):
    """
    Background task to sync global prices for a specific SKU.
    """
    from accounts.models import Tenant
    from main.models import Product
    from decimal import Decimal
    
    try:
        tenant = Tenant.objects.get(id=tenant_id)
        price_decimal = Decimal(new_price)
        
        # Find all products with this SKU in this tenant's branches
        updated_count = Product.objects.filter(
            tenant=tenant,
            sku=sku
        ).update(price=price_decimal)
        
        return f"Successfully updated price for {updated_count} instances of SKU: {sku}"
    except Exception as e:
        return f"Price sync failed: {str(e)}"

@shared_task
def send_webhook_task(url, data, retries=0):
    """
    Background task to send webhooks with retry logic.
    """
    import requests
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        return f"Webhook sent to {url}: {response.status_code}"
    except Exception as e:
        if retries < 3:
            # Retry in 60 seconds
            send_webhook_task.apply_async((url, data, retries + 1), countdown=60)
            return f"Webhook failed, retrying in 60s. Error: {str(e)}"
        else:
            return f"Webhook failed after retries. Error: {str(e)}"

@shared_task
def nightly_inventory_analysis():
    """
    Periodic task to run AI inventory analysis for all tenants.
    """
    from accounts.models import Tenant
    from branches.services.inventory_ai import InventoryAIService
    
    tenants = Tenant.objects.all()
    results = []
    
    from django_tenants.utils import schema_context
    
    for tenant in tenants:
        if tenant.schema_name == 'public':
            continue
            
        with schema_context(tenant.schema_name):
            service = InventoryAIService(tenant)
            results.append({
                'tenant': tenant.name,
                'analysis': service.run_analysis()
            })
    
    return results


@shared_task
def check_low_stock():
    """
    Periodic task to check stock levels and create alerts.
    Runs every hour to monitor inventory across all branches.
    """
    from main.services.alert_service import check_stock_levels
    
    try:
        alerts_created = check_stock_levels()
        return f"Stock check complete. Created {len(alerts_created)} alerts."
    except Exception as e:
        return f"Error checking stock levels: {str(e)}"
@shared_task
def sync_exchange_rates():
    """
    Periodic task to fetch latest exchange rates and update all tenants.
    """
    import requests
    from accounts.models import Tenant
    from main.services.currency_service import update_exchange_rates, BASE_CURRENCY
    from django_tenants.utils import schema_context
    
    # Fetch once for all tenants
    api_url = f"https://api.exchangerate-api.com/v4/latest/{BASE_CURRENCY}"
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            rates = response.json().get('rates', {})
            
            tenants = Tenant.objects.all()
            updated_count = 0
            
            for tenant in tenants:
                if tenant.schema_name == 'public':
                    continue
                    
                with schema_context(tenant.schema_name):
                    if update_exchange_rates(rates=rates):
                        updated_count += 1
            
            return f"Successfully updated exchange rates for {updated_count} tenants."
    except Exception as e:
        return f"Failed to sync exchange rates: {str(e)}"
    
    return "No rates fetched or updated."
    
@shared_task
def process_marketing_automation():
    """
    Periodic task to check for birthday and inactivity triggers.
    Runs daily or hourly.
    """
    from accounts.models import Tenant
    from main.services.marketing_service import check_periodic_triggers
    from django_tenants.utils import schema_context
    
    tenants = Tenant.objects.all()
    for tenant in tenants:
        if tenant.schema_name == 'public':
            continue
        with schema_context(tenant.schema_name):
            check_periodic_triggers()
    return "Marketing automation check complete."

@shared_task
def process_scheduled_manual_campaigns():
    """
    Periodic task to send scheduled manual campaigns.
    Runs every 15 mins.
    """
    from accounts.models import Tenant
    from main.services.marketing_service import process_scheduled_campaigns
    from django_tenants.utils import schema_context
    
    tenants = Tenant.objects.all()
    for tenant in tenants:
        if tenant.schema_name == 'public':
            continue
        with schema_context(tenant.schema_name):
            process_scheduled_campaigns()
    return "Scheduled campaigns processed."
