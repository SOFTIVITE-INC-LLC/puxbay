#!/usr/bin/env python
"""
Debug script to check subscription status of all tenants
"""
import os
import sys
import django

# Add the project directory to the path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from accounts.models import Tenant
from billing.models import Subscription
from billing.utils import is_subscription_active

print("=" * 80)
print("TENANT SUBSCRIPTION STATUS CHECK")
print("=" * 80)
print()

tenants = Tenant.objects.all()

for tenant in tenants:
    print(f"Tenant: {tenant.name} ({tenant.subdomain})")
    print("-" * 80)
    
    # Check if subscription exists
    try:
        subscription = tenant.subscription
        print(f"  Subscription ID: {subscription.id}")
        print(f"  Plan: {subscription.plan.name if subscription.plan else 'No Plan'}")
        print(f"  Status: {subscription.status}")
        print(f"  Current Period End: {subscription.current_period_end}")
        print(f"  Cancel at Period End: {subscription.cancel_at_period_end}")
    except Subscription.DoesNotExist:
        print(f"  ❌ NO SUBSCRIPTION FOUND")
        subscription = None
    
    # Check if subscription is active
    is_active = is_subscription_active(tenant)
    print(f"  Is Active (via utility): {'✅ YES' if is_active else '❌ NO'}")
    
    # Show what middleware would do
    if is_active:
        print(f"  ➡️  Middleware Action: ALLOW ACCESS")
    else:
        print(f"  ➡️  Middleware Action: BLOCK ACCESS → redirect to subscription_required")
    
    print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)

active_count = sum(1 for t in tenants if is_subscription_active(t))
total_count = tenants.count()

print(f"Total Tenants: {total_count}")
print(f"Active Subscriptions: {active_count}")
print(f"Inactive/No Subscription: {total_count - active_count}")
print()

if active_count == total_count:
    print("⚠️  ALL TENANTS HAVE ACTIVE SUBSCRIPTIONS!")
    print("   This is why they can access the dashboard.")
    print()
    print("To test the blocking feature:")
    print("1. Create a new tenant account (register)")
    print("2. Do NOT subscribe to any plan")
    print("3. Try to access /dashboard/")
    print()
    print("OR manually expire a subscription:")
    print("   - Go to Django admin: /admin/")
    print("   - Find a Subscription")
    print("   - Change status to 'canceled' or set current_period_end to a past date")
