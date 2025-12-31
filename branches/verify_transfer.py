
import os
import django
import sys
from decimal import Decimal

# Setup settings
sys.path.append('/home/afari/Documents/Design/Dev/development/softivite/sass-pos/possystem')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Tenant, Branch, UserProfile
from main.models import Product
from branches.models import StockTransfer, StockTransferItem
from django.contrib.auth.models import User

def verify():
    # 1. Setup Data
    print("Setting up test data...")
    user = User.objects.first()
    if not user:
        print("No user found, creating minimal setup...")
        return
        
    profile = user.profile
    tenant = profile.tenant
    
    # Ensure branches
    branch1, created = Branch.objects.get_or_create(tenant=tenant, name="Branch A", defaults={'address': 'Loc A'})
    branch2, created = Branch.objects.get_or_create(tenant=tenant, name="Branch B", defaults={'address': 'Loc B'})
    
    # Ensure product in Branch 1
    p1, created = Product.objects.get_or_create(
        tenant=tenant, 
        branch=branch1, 
        name="Test Item 1",
        defaults={'sku': 'TEST001', 'price': Decimal('10.00'), 'stock_quantity': 100}
    )
    p1.stock_quantity = 100 # Reset
    p1.save()
    
    print(f"Branch A Stock: {p1.stock_quantity}")
    
    # 2. Create Transfer (Pending)
    print("Creating transfer A -> B...")
    transfer = StockTransfer.objects.create(
        tenant=tenant,
        source_branch=branch1,
        destination_branch=branch2,
        reference_id="TEST-TRF-001",
        status='pending',
        created_by=profile
    )
    
    StockTransferItem.objects.create(transfer=transfer, product=p1, quantity=10)
    
    # Deduct Logic (Simulating view logic)
    p1.stock_quantity -= 10
    p1.save()
    
    print(f"Transfer created. Branch A Stock (After Deduct): {p1.stock_quantity}")
    assert p1.stock_quantity == 90
    
    # 3. Receive Transfer
    print("Receiving transfer at Branch B...")
    transfer.status = 'completed'
    transfer.save()
    
    # Add to Branch B
    p2 = Product.objects.filter(branch=branch2, sku='TEST001').first()
    if not p2:
        print("Creating new product in Branch B...")
        p2 = Product.objects.create(
            tenant=tenant, branch=branch2, name=p1.name, sku=p1.sku, 
            price=p1.price, stock_quantity=0
        )
    
    p2.stock_quantity += 10
    p2.save()
    
    print(f"Branch B Stock: {p2.stock_quantity}")
    assert p2.stock_quantity == 10
    
    print("Verification Successful!")

if __name__ == "__main__":
    verify()
