"""
Quick diagnostic script to check subscription enforcement
Run this to see what's happening with subscriptions
"""
from django.contrib.auth.models import User
from accounts.models import Tenant, UserProfile
from billing.models import Subscription
from billing.utils import is_subscription_active

print("=" * 80)
print("SUBSCRIPTION DIAGNOSTIC")
print("=" * 80)
print()

# Check all tenants
tenants = Tenant.objects.all()
print(f"Total Tenants: {tenants.count()}")
print()

for tenant in tenants:
    print(f"Tenant: {tenant.name} ({tenant.subdomain})")
    print("-" * 80)
    
    # Check subscription
    try:
        subscription = tenant.subscription
        print(f"  ✓ Has Subscription")
        print(f"    Plan: {subscription.plan.name if subscription.plan else 'No Plan'}")
        print(f"    Status: {subscription.status}")
        print(f"    Period End: {subscription.current_period_end}")
    except Subscription.DoesNotExist:
        print(f"  ✗ NO SUBSCRIPTION")
        subscription = None
    
    # Check if active
    is_active = is_subscription_active(tenant)
    print(f"  Is Active: {'✅ YES' if is_active else '❌ NO'}")
    
    # Check users
    users = UserProfile.objects.filter(tenant=tenant)
    print(f"  Users: {users.count()}")
    for profile in users:
        print(f"    - {profile.user.username} ({profile.role})")
    
    # Middleware action
    if is_active:
        print(f"  🟢 Middleware: ALLOW dashboard access")
    else:
        print(f"  🔴 Middleware: BLOCK dashboard access → redirect to subscription_required")
    
    print()

print("=" * 80)
print("MIDDLEWARE CHECK")
print("=" * 80)

# Check if middleware is in settings
import possystem.settings as settings
middleware_list = settings.MIDDLEWARE

if 'billing.middleware.SubscriptionMiddleware' in middleware_list:
    print("✅ SubscriptionMiddleware is ACTIVE")
    index = middleware_list.index('billing.middleware.SubscriptionMiddleware')
    print(f"   Position: {index + 1} of {len(middleware_list)}")
else:
    print("❌ SubscriptionMiddleware is NOT in MIDDLEWARE list!")

print()
print("Middleware order:")
for i, mw in enumerate(middleware_list, 1):
    marker = "👉" if "Subscription" in mw else "  "
    print(f"{marker} {i}. {mw}")

print()
print("=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

# Count active vs inactive
active_count = sum(1 for t in tenants if is_subscription_active(t))
inactive_count = tenants.count() - active_count

if inactive_count == 0:
    print("⚠️  ALL tenants have active subscriptions!")
    print("   To test blocking:")
    print("   1. Go to /admin/billing/subscription/")
    print("   2. Find a subscription")
    print("   3. Change status to 'canceled'")
    print("   4. Save and try accessing /dashboard/")
else:
    print(f"✓ Found {inactive_count} tenant(s) without active subscriptions")
    print("  They should be blocked from /dashboard/")
    print()
    print("  If they can still access, check:")
    print("  1. Are they logging in as superuser? (superusers bypass)")
    print("  2. Check terminal logs when accessing /dashboard/")
    print("  3. Verify middleware is running (check for [SUBSCRIPTION CHECK] logs)")
