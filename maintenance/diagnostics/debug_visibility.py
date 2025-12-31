import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Tenant
from django_tenants.utils import schema_context

def debug_tenant_visibility(schema_name):
    print(f"\n--- Checking visibility for schema: {schema_name} ---")
    
    # 1. Public context
    print(f"1. Context: public")
    print(f"   connection.schema_name: {connection.schema_name}")
    with connection.cursor() as cursor:
        cursor.execute("SHOW search_path")
        print(f"   search_path: {cursor.fetchone()[0]}")
    
    tenants = list(Tenant.objects.all())
    print(f"   Tenants found: {[t.schema_name for t in tenants]}")
    
    # 2. Tenant context
    print(f"\n2. Context: {schema_name}")
    with schema_context(schema_name):
        print(f"   connection.schema_name: {connection.schema_name}")
        with connection.cursor() as cursor:
            cursor.execute("SHOW search_path")
            print(f"   search_path: {cursor.fetchone()[0]}")
        
        try:
            tenants = list(Tenant.objects.all())
            print(f"   Tenants found: {[t.schema_name for t in tenants]}")
        except Exception as e:
            print(f"   Error listing tenants: {e}")
            
        try:
            t = Tenant.objects.get(schema_name=schema_name)
            print(f"   Found tenant {schema_name} by get(): YES")
        except Exception as e:
            print(f"   Error getting tenant {schema_name}: {e}")

debug_tenant_visibility('eduscope')
debug_tenant_visibility('softiviteinc')
