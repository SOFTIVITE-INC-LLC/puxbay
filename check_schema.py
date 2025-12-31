import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Tenant
from django.db import connection

# Check softivite schema
tenant = Tenant.objects.get(schema_name='softivite')
connection.set_tenant(tenant)

cursor = connection.cursor()
cursor.execute("""
    SELECT tablename 
    FROM pg_tables 
    WHERE schemaname = 'softivite' 
    AND tablename LIKE 'main_%' 
    ORDER BY tablename
""")

tables = [r[0] for r in cursor.fetchall()]
print(f"Tables in softivite schema (main_*):")
for table in tables:
    print(f"  - {table}")

if not tables:
    print("  ❌ NO TABLES FOUND!")
    print("\nChecking if main app is in TENANT_APPS...")
    from django.conf import settings
    print(f"  TENANT_APPS: {settings.TENANT_APPS}")
