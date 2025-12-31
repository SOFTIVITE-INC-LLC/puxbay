import os
import django
from django.db import connection
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

def find_shadow_tables():
    print("--- Shadow Table Audit ---")
    
    with connection.cursor() as cursor:
        # Get tables in public
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        public_tables = {row[0] for row in cursor.fetchall()}
        
        # Get schemas
        cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('public', 'information_schema', 'pg_catalog')")
        tenant_schemas = [row[0] for row in cursor.fetchall()]
        
        for schema in tenant_schemas:
            print(f"\nAudit for schema: {schema}")
            cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'")
            tenant_tables = {row[0] for row in cursor.fetchall()}
            
            shadow_tables = public_tables.intersection(tenant_tables)
            # Exclude django_migrations as it's often present in both
            shadow_tables.discard('django_migrations')
            
            if shadow_tables:
                print(f"   Found {len(shadow_tables)} shadow tables that should likely be dropped:")
                for table in sorted(list(shadow_tables)):
                    cursor.execute(f"SELECT count(*) FROM {schema}.{table}")
                    count = cursor.fetchone()[0]
                    print(f"    - {table} ({count} rows)")
            else:
                print("   No shadow tables found.")

if __name__ == "__main__":
    find_shadow_tables()
