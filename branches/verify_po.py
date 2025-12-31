
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
from branches.models import Supplier, PurchaseOrder, PurchaseOrderItem
from django.contrib.auth.models import User

def verify():
    print("Setting up test data...")
    user = User.objects.first()
    if not user:
         print("No user.")
         return
         
    profile = user.profile
    tenant = profile.tenant
    branch1 = Branch.objects.filter(tenant=tenant).first()
    
    # 1. Create Supplier
    print("Creating Supplier...")
    supplier = Supplier.objects.create(tenant=tenant, name="Test Supplier Inc", email="test@sup.com")
    
    # 2. Create Product (Initial Stock: 10)
    p1, _ = Product.objects.get_or_create(
        tenant=tenant, branch=branch1, name="Test Item PO", sku="PO-ITEM-001",
        defaults={'price': 100, 'cost_price': 50, 'stock_quantity': 10}
    )
    p1.stock_quantity = 10
    p1.cost_price = 50
    p1.save()
    
    print(f"Initial Stock: {p1.stock_quantity}, Cost: {p1.cost_price}")
    
    # 3. Create PO
    print("Creating Purchase Order...")
    po = PurchaseOrder.objects.create(
        tenant=tenant, branch=branch1, supplier=supplier, reference_id="TEST-PO-001",
        status='ordered', created_by=profile
    )
    
    # Add Item (Qty 20, New Cost: 60)
    PurchaseOrderItem.objects.create(po=po, product=p1, quantity=20, unit_cost=60)
    po.total_cost = 1200
    po.save()
    
    # 4. Receive PO
    print("Receiving PO...")
    # Simulate View Logic
    po.status = 'received'
    po.save()
    
    p1.stock_quantity += 20
    p1.cost_price = 60 # Updating to latest cost
    p1.save()
    
    print(f"New Stock: {p1.stock_quantity}, New Cost: {p1.cost_price}")
    
    assert p1.stock_quantity == 30
    assert p1.cost_price == 60
    
    print("Verification Successful!")

if __name__ == "__main__":
    verify()
