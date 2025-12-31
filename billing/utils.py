"""
Utility functions for currency exchange rates
"""
import requests
from decimal import Decimal
from django.core.cache import cache

def get_usd_to_ghs_rate():
    """
    Get current USD to GHS exchange rate.
    Uses exchangerate-api.com (free tier: 1500 requests/month)
    Caches the rate for 1 hour to avoid excessive API calls.
    """
    cache_key = 'usd_to_ghs_rate'
    
    # Try to get from cache first
    cached_rate = cache.get(cache_key)
    if cached_rate:
        return Decimal(str(cached_rate))
    
    try:
        # Free API - no key required for basic usage
        url = 'https://api.exchangerate-api.com/v4/latest/USD'
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            rate = data['rates'].get('GHS')
            
            if rate:
                # Cache for 1 hour (3600 seconds)
                cache.set(cache_key, rate, 3600)
                return Decimal(str(rate))
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
    
    # Fallback to a default rate if API fails
    fallback_rate = 11.48
    return Decimal(str(fallback_rate))


# Subscription Management Functions

def get_tenant_subscription(tenant):
    """
    Get the active subscription for a tenant.
    Returns None if no subscription exists.
    """
    from billing.models import Subscription
    try:
        return tenant.subscription
    except Subscription.DoesNotExist:
        return None


def is_subscription_active(tenant):
    """
    Check if tenant has an active or trialing subscription.
    Uses schema_context('public') to ensure shared models (Subscription, Plan) are visible.
    """
    from django.utils import timezone
    from django_tenants.utils import schema_context
    from billing.models import Subscription
    
    with schema_context('public'):
        try:
            # We want to use the ID to be safe
            subscription = Subscription.objects.select_related('plan').filter(tenant_id=tenant.id).first()
        except Exception:
            return False

        if not subscription:
            return False
        
        # Check if subscription is active or trialing
        if subscription.status in ['active', 'trialing']:
            # Ensure a plan is assigned
            if not subscription.plan:
                return False
                
            # Check if trial/period hasn't ended
            if subscription.current_period_end:
                now = timezone.now()
                return subscription.current_period_end > now
            
            return True
        
        return False


def check_branch_limit(tenant):
    """
    Check if tenant can create more branches.
    Returns (can_create: bool, current_count: int, max_allowed: int)
    """
    from accounts.models import Branch
    
    subscription = get_tenant_subscription(tenant)
    if not subscription or not subscription.plan:
        return False, 0, 0
    
    current_count = Branch.objects.filter(tenant=tenant).count()
    max_allowed = subscription.plan.max_branches
    
    can_create = current_count < max_allowed
    return can_create, current_count, max_allowed


def check_user_limit(tenant):
    """
    Check if tenant can create more users.
    Returns (can_create: bool, current_count: int, max_allowed: int)
    """
    from accounts.models import UserProfile
    
    subscription = get_tenant_subscription(tenant)
    if not subscription or not subscription.plan:
        return False, 0, 0
    
    current_count = UserProfile.objects.filter(tenant=tenant).count()
    max_allowed = subscription.plan.max_users
    
    can_create = current_count < max_allowed
    return can_create, current_count, max_allowed
