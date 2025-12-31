import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Tenant, Branch
from main.models import Product
from branches.xlsx_utils import XLSXGenerator

def create_sample_template():
    """Create a sample product import template"""
    generator = XLSXGenerator()
    
    # Headers
    headers = [
        'Product Name', 'SKU', 'Category', 'Price', 'Wholesale Price',
        'Min Wholesale Qty', 'Cost Price', 'Stock Quantity', 'Low Stock Threshold',
        'Barcode', 'Expiry Date', 'Batch Number', 'Invoice/Waybill',
        'Description', 'Active', 'Image URL', 'Manufacturing Date',
        'Country of Origin', 'Manufacturer Name', 'Manufacturer Address'
    ]
    generator.writerow(headers)
    
    # Sample products
    sample_products = [
        ['Coca Cola 500ml', 'COKE500', 'Beverages', '5.00', '4.50', '12', '3.50', '100', '20',
         '123456789', '', 'BATCH001', 'INV-001', 'Refreshing cola drink', 'TRUE', '', '',
         'USA', 'Coca Cola Company', '123 Main St, Atlanta, GA'],
        
        ['Fanta Orange 500ml', 'FANTA500', 'Beverages', '5.00', '4.50', '12', '3.50', '80', '20',
         '987654321', '', 'BATCH002', 'INV-001', 'Orange flavored soda', 'TRUE', '', '',
         'USA', 'Coca Cola Company', '123 Main St, Atlanta, GA'],
    ]
    
    for product in sample_products:
        generator.writerow(product)
    
    return generator.generate()

def test_with_real_file():
    print("Creating sample XLSX file...")
    xlsx_bytes = create_sample_template()
    
    # Save to file for manual testing
    with open('sample_products.xlsx', 'wb') as f:
        f.write(xlsx_bytes)
    print(f"✓ Created sample_products.xlsx ({len(xlsx_bytes)} bytes)")
    
    # Test import
    print("\nTesting import...")
    tenant = Tenant.objects.exclude(schema_name='public').first()
    branch = Branch.objects.filter(tenant=tenant).first()
    
    print(f"Tenant: {tenant.name}, Branch: {branch.name}")
    
    # Use tenant context for queries
    from django_tenants.utils import tenant_context
    
    with tenant_context(tenant):
        # Count products before
        before_count = Product.objects.filter(branch=branch).count()
        print(f"Products before: {before_count}")
    
    # Import using the task
    from branches.tasks import import_products_task
    import base64
    
    file_content_b64 = base64.b64encode(xlsx_bytes).decode('utf-8')
    
    try:
        result = import_products_task(
            str(tenant.id),
            str(branch.id),
            file_content_b64
        )
        print(f"✓ Import result: {result}")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
    
    with tenant_context(tenant):
        # Count products after
        after_count = Product.objects.filter(branch=branch).count()
        print(f"Products after: {after_count}")
        print(f"New products: {after_count - before_count}")

if __name__ == "__main__":
    test_with_real_file()
