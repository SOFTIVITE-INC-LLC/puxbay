"""
Script to clean users, tenants, and subscriptions from the database.
This will allow testing subscription enforcement from scratch.
"""
from django.contrib.auth.models import User
from accounts.models import Tenant, UserProfile, Branch, Attendance, ActivityLog
from billing.models import Subscription, Payment, Plan
from main.models import *
from branches.models import *

print("=" * 80)
print("DATABASE CLEANUP SCRIPT")
print("=" * 80)
print()

# Ask for confirmation
print("⚠️  WARNING: This will delete ALL data except Plans!")
print()
print("The following will be deleted:")
print("  - All Users (except superusers)")
print("  - All Tenants")
print("  - All Branches")
print("  - All Subscriptions")
print("  - All Orders, Products, Customers")
print("  - All Activity Logs")
print()
print("Plans will be PRESERVED so you can subscribe to them.")
print()

# Count current data
user_count = User.objects.filter(is_superuser=False).count()
tenant_count = Tenant.objects.count()
subscription_count = Subscription.objects.count()
branch_count = Branch.objects.count()
order_count = Order.objects.count()
product_count = Product.objects.count()
customer_count = Customer.objects.count()

print(f"Current Database Stats:")
print(f"  Users (non-superuser): {user_count}")
print(f"  Tenants: {tenant_count}")
print(f"  Subscriptions: {subscription_count}")
print(f"  Branches: {branch_count}")
print(f"  Orders: {order_count}")
print(f"  Products: {product_count}")
print(f"  Customers: {customer_count}")
print()

# Perform deletion
print("Starting cleanup...")
print()

# Delete in correct order to avoid foreign key constraints

# 1. Delete activity logs
deleted = ActivityLog.objects.all().delete()
print(f"✓ Deleted {deleted[0]} activity logs")

# 2. Delete attendance records
deleted = Attendance.objects.all().delete()
print(f"✓ Deleted {deleted[0]} attendance records")

# 3. Delete orders and related items
deleted = OrderItem.objects.all().delete()
print(f"✓ Deleted {deleted[0]} order items")
deleted = Order.objects.all().delete()
print(f"✓ Deleted {deleted[0]} orders")

# 4. Delete products and categories
deleted = Product.objects.all().delete()
print(f"✓ Deleted {deleted[0]} products")
deleted = Category.objects.all().delete()
print(f"✓ Deleted {deleted[0]} categories")

# 5. Delete customers
deleted = Customer.objects.all().delete()
print(f"✓ Deleted {deleted[0]} customers")

# 6. Delete inventory-related data
from branches.models import StockBatch, StockMovement, StockTransfer, StockTransferItem
from branches.models import Supplier, PurchaseOrder, PurchaseOrderItem, CashDrawerSession

deleted = StockMovement.objects.all().delete()
print(f"✓ Deleted {deleted[0]} stock movements")
deleted = StockTransferItem.objects.all().delete()
print(f"✓ Deleted {deleted[0]} stock transfer items")
deleted = StockTransfer.objects.all().delete()
print(f"✓ Deleted {deleted[0]} stock transfers")
deleted = StockBatch.objects.all().delete()
print(f"✓ Deleted {deleted[0]} stock batches")
deleted = PurchaseOrderItem.objects.all().delete()
print(f"✓ Deleted {deleted[0]} purchase order items")
deleted = PurchaseOrder.objects.all().delete()
print(f"✓ Deleted {deleted[0]} purchase orders")
deleted = Supplier.objects.all().delete()
print(f"✓ Deleted {deleted[0]} suppliers")
deleted = CashDrawerSession.objects.all().delete()
print(f"✓ Deleted {deleted[0]} cash drawer sessions")

# 7. Delete subscriptions and payments
deleted = Payment.objects.all().delete()
print(f"✓ Deleted {deleted[0]} payments")
deleted = Subscription.objects.all().delete()
print(f"✓ Deleted {deleted[0]} subscriptions")

# 8. Delete branches
deleted = Branch.objects.all().delete()
print(f"✓ Deleted {deleted[0]} branches")

# 9. Delete user profiles
deleted = UserProfile.objects.all().delete()
print(f"✓ Deleted {deleted[0]} user profiles")

# 10. Delete tenants
deleted = Tenant.objects.all().delete()
print(f"✓ Deleted {deleted[0]} tenants")

# 11. Delete non-superuser users
deleted = User.objects.filter(is_superuser=False).delete()
print(f"✓ Deleted {deleted[0]} users (preserved superusers)")

print()
print("=" * 80)
print("CLEANUP COMPLETE!")
print("=" * 80)
print()

# Show remaining data
superuser_count = User.objects.filter(is_superuser=True).count()
plan_count = Plan.objects.count()

print("Remaining Data:")
print(f"  Superusers: {superuser_count}")
print(f"  Plans: {plan_count}")
print()

if plan_count == 0:
    print("⚠️  No plans found! Run: python manage.py shell < populate_pricing.py")
else:
    print("Available Plans:")
    for plan in Plan.objects.all():
        print(f"  - {plan.name}: ${plan.price}/{plan.interval}")

print()
print("✅ Database is now clean and ready for testing!")
print()
print("Next Steps:")
print("1. Register a new tenant account")
print("2. Do NOT subscribe to any plan")
print("3. Try to access /dashboard/")
print("4. You should be redirected to /billing/subscription-required/")
print()
