import os
import django
from django.db import connection

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

def check_constraints():
    print("Checking Foreign Key Constraints for 'accounts_activitylog'...")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                tc.constraint_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                rc.update_rule,
                rc.delete_rule
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
                JOIN information_schema.referential_constraints AS rc
                  ON rc.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
              AND tc.table_name='accounts_activitylog';
        """)
        
        rows = cursor.fetchall()
        for row in rows:
            print(f"Constraint: {row[0]}")
            print(f"  Column: {row[1]}")
            print(f"  Ref Table: {row[2]}")
            print(f"  On Update: {row[4]}")
            print(f"  On Delete: {row[5]}")
            print("-" * 20)

if __name__ == "__main__":
    check_constraints()
