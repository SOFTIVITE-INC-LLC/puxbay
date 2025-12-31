import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

def check_remaining_shadows():
    print("--- Checking for Non-Empty Shadow Tables ---")
    with connection.cursor() as cursor:
        cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('public', 'information_schema', 'pg_catalog')")
        schemas = [row[0] for row in cursor.fetchall()]
        
        critical_tables = ['auth_user', 'accounts_userprofile', 'accounts_tenant', 'billing_subscription']
        
        for schema in schemas:
            print(f"\nSchema: {schema}")
            for table in critical_tables:
                cursor.execute(f"SELECT exists(SELECT 1 FROM information_schema.tables WHERE table_schema='{schema}' AND table_name='{table}')")
                if cursor.fetchone()[0]:
                    cursor.execute(f"SELECT count(*) FROM {schema}.{table}")
                    count = cursor.fetchone()[0]
                    print(f"  [SHADOW FOUND] {table}: {count} rows")
                else:
                    print(f"  {table}: Clean")

if __name__ == "__main__":
    check_remaining_shadows()
