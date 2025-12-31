import os
import django
import base64

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Tenant, Branch
from main.models import Product
from branches.tasks import import_products_task
from django_tenants.utils import tenant_context

def test_300_import():
    print("Testing import of 300-product file...")
    
    # Read the generated file
    if not os.path.exists('sample_products_300.xlsx'):
        print("❌ File not found: sample_products_300.xlsx")
        print("   Run generate_sample_data.py first!")
        return
    
    with open('sample_products_300.xlsx', 'rb') as f:
        file_content = f.read()
    
    print(f"✓ Loaded file ({len(file_content)} bytes)")
    
    # Get tenant and branch
    tenant = Tenant.objects.exclude(schema_name='public').first()
    branch = Branch.objects.filter(tenant=tenant).first()
    
    print(f"✓ Tenant: {tenant.name} ({tenant.schema_name})")
    print(f"✓ Branch: {branch.name}")
    
    # Count before
    with tenant_context(tenant):
        before_count = Product.objects.filter(branch=branch).count()
        print(f"✓ Products before: {before_count}")
    
    # Encode and import
    file_content_b64 = base64.b64encode(file_content).decode('utf-8')
    
    print("\n🚀 Starting import task...")
    try:
        result = import_products_task(
            str(tenant.id),
            str(branch.id),
            file_content_b64
        )
        print(f"\n✅ Import completed!")
        print(f"   Success: {result['success']}")
        print(f"   Errors: {result['errors']}")
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Count after
    with tenant_context(tenant):
        after_count = Product.objects.filter(branch=branch).count()
        print(f"\n✓ Products after: {after_count}")
        print(f"✓ New products imported: {after_count - before_count}")
        
        # Show some sample products
        if after_count > before_count:
            print("\n📦 Sample imported products:")
            recent = Product.objects.filter(branch=branch).order_by('-created_at')[:5]
            for p in recent:
                print(f"   - {p.name} (SKU: {p.sku}, Price: {p.price})")

if __name__ == "__main__":
    test_300_import()
