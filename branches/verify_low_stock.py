
import os
import django
import sys

# Setup settings
sys.path.append('/home/afari/Documents/Design/Dev/development/softivite/sass-pos/possystem')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Branch
from main.models import Product
from django.contrib.auth.models import User

def verify():
    print("Setting up test data...")
    user = User.objects.first()
    if not user: return
    
    tenant = user.profile.tenant
    branch = Branch.objects.filter(tenant=tenant).first()
    
    # Create Product with Low Stock
    p1, _ = Product.objects.get_or_create(
        tenant=tenant, branch=branch, name="Low Stock Item", sku="LOW-001",
        defaults={'price': 10, 'stock_quantity': 5, 'low_stock_threshold': 10}
    )
    p1.stock_quantity = 5
    p1.low_stock_threshold = 10
    p1.save()
    
    # Create Product with High Stock
    p2, _ = Product.objects.get_or_create(
        tenant=tenant, branch=branch, name="High Stock Item", sku="HIGH-001",
        defaults={'price': 10, 'stock_quantity': 20, 'low_stock_threshold': 10}
    )
    p2.stock_quantity = 20
    p2.low_stock_threshold = 10
    p2.save()
    
    # Verify Logic
    from django.db.models import F
    low_stock = Product.objects.filter(
        branch=branch, 
        stock_quantity__lte=F('low_stock_threshold')
    )
    
    print(f"Low Stock Count: {low_stock.count()}")
    assert low_stock.count() >= 1
    assert p1 in low_stock
    assert p2 not in low_stock
    
    print("Verification Successful!")

if __name__ == "__main__":
    verify()
