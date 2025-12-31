import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

def audit_tables():
    print("--- Comprehensive Table Audit ---")
    with connection.cursor() as cursor:
        cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog')")
        schemas = [row[0] for row in cursor.fetchall()]
        
        for schema in schemas:
            print(f"\nSchema: {schema}")
            cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in sorted(tables):
                try:
                    cursor.execute(f"SELECT count(*) FROM {schema}.{table}")
                    count = cursor.fetchone()[0]
                    if count > 0 or table in ['auth_user', 'accounts_userprofile', 'accounts_tenant']:
                        print(f"  {table}: {count} rows")
                except Exception as e:
                    print(f"  {table}: Error ({e})")

if __name__ == "__main__":
    audit_tables()
