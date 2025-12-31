import os
import django
from django.db import connection, transaction
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

def normalize_schemas():
    print("--- Database Schema Normalization (Fixing Shadows) ---")
    
    from django.conf import settings
    shared_apps = set(settings.SHARED_APPS)
    tenant_apps = set(settings.TENANT_APPS)
    
    # Correct mapping: full app name (as in settings) to its tables
    shared_app_tables = []
    tenant_app_tables = []
    
    for app_config in apps.get_app_configs():
        # Check if the app's full name (e.g. 'django.contrib.auth') is in shared/tenant apps
        app_name = app_config.name
        tables = [model._meta.db_table for model in app_config.get_models()]
        
        if app_name in shared_apps:
            shared_app_tables.extend(tables)
            print(f"Mapped SHARED app: {app_name} -> {len(tables)} tables")
        elif app_name in tenant_apps:
            tenant_app_tables.extend(tables)
            print(f"Mapped TENANT app: {app_name} -> {len(tables)} tables")
        else:
            # Check by label as fallback (some apps use labels in settings)
            if app_config.label in shared_apps:
                shared_app_tables.extend(tables)
                print(f"Mapped SHARED app (by label): {app_config.label} -> {len(tables)} tables")
            elif app_config.label in tenant_apps:
                tenant_app_tables.extend(tables)
                print(f"Mapped TENANT app (by label): {app_config.label} -> {len(tables)} tables")

    with connection.cursor() as cursor:
        cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog')")
        all_schemas = [row[0] for row in cursor.fetchall()]
        tenant_schemas = [s for s in all_schemas if s != 'public']
        
        # 1. Clean up PUBLIC schema (remove TENANT_APP tables)
        print("\n[STEP 1] Cleaning up PUBLIC schema...")
        for table in set(tenant_app_tables):
            cursor.execute(f"SELECT exists(SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='{table}')")
            if cursor.fetchone()[0]:
                print(f"   Dropping public.{table}...")
                cursor.execute(f"DROP TABLE public.{table} CASCADE")

        # 2. Clean up TENANT schemas (remove SHARED_APP tables)
        print("\n[STEP 2] Cleaning up TENANT schemas...")
        for schema in tenant_schemas:
            print(f" Processing schema: {schema}")
            for table in set(shared_app_tables):
                cursor.execute(f"SELECT exists(SELECT 1 FROM information_schema.tables WHERE table_schema='{schema}' AND table_name='{table}')")
                if cursor.fetchone()[0]:
                    # For shared tables in tenant schemas, we are more aggressive if they are empty
                    cursor.execute(f"SELECT count(*) FROM {schema}.{table}")
                    count = cursor.fetchone()[0]
                    
                    # Special cases: auth_user, accounts_tenant, etc should NEVER be in a tenant schema
                    critical_shared = ['auth_user', 'accounts_tenant', 'accounts_userprofile', 'billing_subscription']
                    
                    if count == 0 or table in critical_shared:
                        print(f"   Dropping {schema}.{table} (Count: {count})...")
                        cursor.execute(f"DROP TABLE {schema}.{table} CASCADE")
                    else:
                        print(f"   WARNING: SKIPPING {schema}.{table} because it has {count} rows!")

    print("\nNormalization complete. Please restart the server.")

    print("\nNormalization complete. Please restart the server.")

if __name__ == "__main__":
    normalize_schemas()
