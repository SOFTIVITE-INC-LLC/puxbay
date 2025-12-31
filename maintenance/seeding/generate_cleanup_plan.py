import os
import django
from django.db import connection
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

def cleanup_schemas():
    print("--- Database Schema Cleanup Plan ---")
    
    from django.conf import settings
    shared_apps = set(settings.SHARED_APPS)
    tenant_apps = set(settings.TENANT_APPS)
    
    # Map app labels to their tables
    app_tables = {}
    for app_config in apps.get_app_configs():
        app_tables[app_config.label] = [model._meta.db_table for model in app_config.get_models()]

    with connection.cursor() as cursor:
        # Get all schemas
        cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog')")
        all_schemas = [row[0] for row in cursor.fetchall()]
        
        tenant_schemas = [s for s in all_schemas if s != 'public']
        
        # 1. Identify tables that shouldn't be in PUBLIC
        print("\nChecking PUBLIC schema for TENANT_APP tables...")
        for app in tenant_apps:
            if app in shared_apps: continue # skip if both (unlikely)
            tables = app_tables.get(app, [])
            for table in tables:
                cursor.execute(f"SELECT exists(SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='{table}')")
                if cursor.fetchone()[0]:
                    print(f"   [DROP] public.{table} (should be in tenant schemas only)")

        # 2. Identify tables that shouldn't be in TENANT SCHEMAS
        print("\nChecking TENANT schemas for SHARED_APP tables...")
        for schema in tenant_schemas:
            print(f" Schema: {schema}")
            for app in shared_apps:
                tables = app_tables.get(app, [])
                for table in tables:
                    cursor.execute(f"SELECT exists(SELECT 1 FROM information_schema.tables WHERE table_schema='{schema}' AND table_name='{table}')")
                    if cursor.fetchone()[0]:
                        print(f"   [DROP] {schema}.{table} (should be in public schema only)")

if __name__ == "__main__":
    cleanup_schemas()
