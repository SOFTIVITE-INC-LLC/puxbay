import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Tenant
from billing.models import Subscription

def test_tenant_context(schema_name):
    print(f"\n{'='*40}")
    print(f"Testing context for schema: {schema_name}")
    print(f"{'='*40}")
    
    # 1. Access in current context (starts as public)
    print(f"Current schema: {connection.schema_name}")
    with connection.cursor() as cursor:
        cursor.execute("SHOW search_path")
        print(f"Search path: {cursor.fetchone()}")
        
    try:
        tenant = Tenant.objects.get(schema_name=schema_name)
        sub = tenant.subscription
        print(f"Subscription in {connection.schema_name} context: FOUND (ID: {sub.id})")
    except Subscription.DoesNotExist:
        print(f"Subscription in {connection.schema_name} context: NOT FOUND")
    except Exception as e:
        print(f"Error in {connection.schema_name} context: {e}")

    # 2. Switch to tenant schema
    print(f"\nSwitching to schema: {schema_name}...")
    from django_tenants.utils import schema_context
    with schema_context(schema_name):
        print(f"Current schema: {connection.schema_name}")
        with connection.cursor() as cursor:
            cursor.execute("SHOW search_path")
            print(f"Search path: {cursor.fetchone()}")
            
        try:
            # Re-fetch tenant in this context
            tenant_in_schema = Tenant.objects.get(schema_name=schema_name)
            sub = tenant_in_schema.subscription
            print(f"Subscription in {connection.schema_name} context: FOUND (ID: {sub.id})")
        except Subscription.DoesNotExist:
            print(f"Subscription in {connection.schema_name} context: NOT FOUND")
        except Exception as e:
            print(f"Error in {connection.schema_name} context: {e}")
            import traceback
            traceback.print_exc()

print("Standalone check (Public context):")
for t in Tenant.objects.all():
    try:
        sub = t.subscription
        print(f" - {t.name} ({t.schema_name}): Sub exists: {sub is not None}")
    except Subscription.DoesNotExist:
        print(f" - {t.name} ({t.schema_name}): Sub exists: False")

test_tenant_context('eduscope')
test_tenant_context('softiviteinc')
