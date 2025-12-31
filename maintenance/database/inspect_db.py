import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

def inspect_database_structure():
    print("--- Detailed Database Table Inspection ---")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT schema_name FROM information_schema.schemata")
        schemas = [row[0] for row in cursor.fetchall()]
        
        # Tables to check for shadowing
        critical_tables = [
            'accounts_tenant', 
            'accounts_userprofile', 
            'auth_user', 
            'billing_subscription',
            'billing_plan'
        ]
        
        print(f"{'Table Name':<30} | {'Found in Public':<15} | {'Found in softiviteinc':<25}")
        print("-" * 75)
        
        for table in critical_tables:
            # Check public
            cursor.execute(f"SELECT exists(SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='{table}')")
            in_public = cursor.fetchone()[0]
            
            # Check softiviteinc
            cursor.execute(f"SELECT exists(SELECT 1 FROM information_schema.tables WHERE table_schema='softiviteinc' AND table_name='{table}')")
            in_tenant = cursor.fetchone()[0]
            
            print(f"{table:<30} | {str(in_public):<15} | {str(in_tenant):<25}")
            
            if in_tenant:
                cursor.execute(f"SELECT count(*) FROM softiviteinc.{table}")
                count = cursor.fetchone()[0]
                print(f"   -> WARNING: {table} exists in softiviteinc with {count} rows!")

if __name__ == "__main__":
    inspect_database_structure()
