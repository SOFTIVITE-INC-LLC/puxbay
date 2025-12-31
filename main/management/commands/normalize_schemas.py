from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps
from django.conf import settings

class Command(BaseCommand):
    help = 'Normalize database schemas by removing redundant "shadow" tables from public and tenant schemas.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("--- Database Schema Normalization (Fixing Shadows) ---"))
        
        shared_apps = set(settings.SHARED_APPS)
        tenant_apps = set(settings.TENANT_APPS)
        
        shared_app_tables = []
        tenant_app_tables = []
        
        for app_config in apps.get_app_configs():
            app_name = app_config.name
            tables = [model._meta.db_table for model in app_config.get_models()]
            
            if app_name in shared_apps:
                shared_app_tables.extend(tables)
            elif app_name in tenant_apps:
                tenant_app_tables.extend(tables)
            else:
                if app_config.label in shared_apps:
                    shared_app_tables.extend(tables)
                elif app_config.label in tenant_apps:
                    tenant_app_tables.extend(tables)

        with connection.cursor() as cursor:
            cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog')")
            all_schemas = [row[0] for row in cursor.fetchall()]
            tenant_schemas = [s for s in all_schemas if s != 'public']
            
            # 1. Clean up PUBLIC schema
            self.stdout.write(self.style.NOTICE("\n[STEP 1] Cleaning up PUBLIC schema..."))
            for table in set(tenant_app_tables):
                cursor.execute(f"SELECT exists(SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='{table}')")
                if cursor.fetchone()[0]:
                    self.stdout.write(f"   Dropping public.{table}...")
                    cursor.execute(f"DROP TABLE public.{table} CASCADE")

            # 2. Clean up TENANT schemas
            self.stdout.write(self.style.NOTICE("\n[STEP 2] Cleaning up TENANT schemas..."))
            for schema in tenant_schemas:
                self.stdout.write(f" Processing schema: {schema}")
                for table in set(shared_app_tables):
                    cursor.execute(f"SELECT exists(SELECT 1 FROM information_schema.tables WHERE table_schema='{schema}' AND table_name='{table}')")
                    if cursor.fetchone()[0]:
                        cursor.execute(f"SELECT count(*) FROM {schema}.{table}")
                        count = cursor.fetchone()[0]
                        
                        critical_shared = ['auth_user', 'accounts_tenant', 'accounts_userprofile', 'billing_subscription']
                        
                        if count == 0 or table in critical_shared:
                            self.stdout.write(f"   Dropping {schema}.{table} (Count: {count})...")
                            cursor.execute(f"DROP TABLE {schema}.{table} CASCADE")
                        else:
                            self.stdout.write(self.style.WARNING(f"   WARNING: SKIPPING {schema}.{table} because it has {count} rows!"))

        self.stdout.write(self.style.SUCCESS("\nNormalization complete. Please restart the server."))
