"""
Quick diagnostic to check product import status

Run this after uploading a file to see what happened
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Tenant, Branch
from main.models import Product
from django_tenants.utils import tenant_context

def show_status():
    print("=" * 60)
    print("PRODUCT IMPORT STATUS CHECK")
    print("=" * 60)
    
    # List all tenants
    tenants = Tenant.objects.exclude(schema_name='public')
    print(f"\n📊 Found {tenants.count()} tenant(s):\n")
    
    for tenant in tenants:
        print(f"\n🏢 Tenant: {tenant.name} ({tenant.schema_name})")
        print("-" * 60)
        
        # Get branches for this tenant
        branches = Branch.objects.filter(tenant=tenant)
        print(f"   Branches: {branches.count()}")
        
        with tenant_context(tenant):
            for branch in branches:
                product_count = Product.objects.filter(branch=branch).count()
                print(f"\n   📍 Branch: {branch.name}")
                print(f"      Products: {product_count}")
                
                if product_count > 0:
                    # Show recent products
                    recent = Product.objects.filter(branch=branch).order_by('-created_at')[:5]
                    print(f"      Recent products:")
                    for p in recent:
                        print(f"         - {p.name} (SKU: {p.sku})")
                else:
                    print(f"      ⚠️  No products found in this branch!")
    
    print("\n" + "=" * 60)
    print("TIP: If you uploaded to a specific branch, make sure you're")
    print("     viewing the SAME branch in the product list page!")
    print("=" * 60)

if __name__ == "__main__":
    show_status()
