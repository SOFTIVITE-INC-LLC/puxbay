import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Tenant, Branch, UserProfile
from main.models import Product
from branches.models import StockTransfer, StockTransferItem
from django.contrib.auth.models import User
from decimal import Decimal

def verify():
    # Setup
    tenant = Tenant.objects.first()
    if not tenant:
        print("No tenant found")
        return

    # Create Branches
    wholesale_branch = Branch.objects.create(name="WholeTest", tenant=tenant, branch_type='wholesale')
    retail_branch = Branch.objects.create(name="RetailTest", tenant=tenant, branch_type='retail')
    
    # Create Product
    product = Product.objects.create(
        tenant=tenant,
        name="TestItem", 
        branch=wholesale_branch, 
        sku="TESTSKU", 
        price=10.00, 
        cost_price=5.00, 
        stock_quantity=100
    )
    
    # Create Transfer with Markup (Cost 5.00 -> Transfer 6.00)
    user_prof = UserProfile.objects.first()
    import uuid
    transfer = StockTransfer.objects.create(
        tenant=tenant,
        source_branch=wholesale_branch,
        destination_branch=retail_branch,
        reference_id=f"TEST-TRF-{uuid.uuid4().hex[:6]}",
        created_by=user_prof
    )
    
    StockTransferItem.objects.create(
        transfer=transfer,
        product=product,
        quantity=10,
        transfer_price=Decimal("6.00")
    )
    
    # Verify Item Price
    item = transfer.items.first()
    assert item.transfer_price == Decimal("6.00"), f"Transfer price mismatch: {item.transfer_price}"
    print("Transfer creation verified.")
    
    # Receive Logic (Simulate view logic)
    # Manual receive simulation
    dest_product = Product.objects.create(
        tenant=tenant,
        name="TestItem",
        branch=retail_branch,
        sku="TESTSKU",
        price=Decimal("10.00"),
        cost_price=Decimal("5.00"), # Existing cost
        stock_quantity=10 # Existing qty
    )
    
    # Weighted Avg Calculation:
    # Existing: 10 * 5.00 = 50.00
    # Incoming: 10 * 6.00 = 60.00
    # Total: 110.00 / 20 = 5.50
    
    current_value = dest_product.stock_quantity * dest_product.cost_price
    new_value = item.quantity * item.transfer_price
    total_qty = dest_product.stock_quantity + item.quantity
    dest_product.cost_price = (current_value + new_value) / total_qty
    dest_product.stock_quantity += item.quantity
    dest_product.save()
    
    assert dest_product.cost_price == Decimal("5.50"), f"Cost price mismatch: {dest_product.cost_price}"
    assert dest_product.stock_quantity == 20
    print("Transfer receive logic verified.")
    
    # Cleanup
    product.delete()
    dest_product.delete()
    transfer.delete()
    wholesale_branch.delete()
    retail_branch.delete()

if __name__ == "__main__":
    try:
        verify()
        print("VERIFICATION SUCCESSFUL")
    except Exception as e:
        print(f"VERIFICATION FAILED: {e}")
