import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Tenant, Branch
from branches.tasks import import_products_task
import base64

# Test data - simple XLSX with one product
# This is a minimal valid XLSX file with headers and one product row
test_xlsx_b64 = """
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
SwUGAAAAAAYABgBnAQAAnwEAAAAA
"""

def test_import():
    print("Testing product import...")
    
    # Get first tenant and branch
    try:
        tenant = Tenant.objects.exclude(schema_name='public').first()
        if not tenant:
            print("❌ No tenant found!")
            return
        
        print(f"✓ Found tenant: {tenant.name} ({tenant.schema_name})")
        
        branch = Branch.objects.filter(tenant=tenant).first()
        if not branch:
            print("❌ No branch found!")
            return
            
        print(f"✓ Found branch: {branch.name}")
        
        # Decode the test XLSX
        file_content_b64 = test_xlsx_b64.strip()
        
        print(f"✓ Calling import task...")
        
        # Call the task directly (not async)
        result = import_products_task(
            str(tenant.id),
            str(branch.id),
            file_content_b64
        )
        
        print(f"✓ Task completed!")
        print(f"  Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_import()
