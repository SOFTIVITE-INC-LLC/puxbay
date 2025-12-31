"""
Middleware to enforce subscription restrictions
"""
from django.shortcuts import redirect
from django.urls import reverse
from billing.utils import is_subscription_active


class SubscriptionMiddleware:
    """
    Middleware to check subscription status on each request.
    Redirects to pricing page if subscription is expired or missing.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs that don't require active subscription
        self.exempt_urls = [
            '/accounts/login/',
            '/accounts/logout/',
            '/accounts/register/',
            '/accounts/signup/',
            '/accounts/branch/',
            '/billing/pricing/',
            '/billing/subscription-required/',
            '/billing/checkout/',
            '/billing/success/',
            '/billing/cancel/',
            '/billing/webhook/',
            '/billing/paystack/',
            '/billing/process/',
            '/admin/',
            '/pricing/',
            '/static/',
            '/media/',
            '/features/',
            '/contact/',
            '/about/',
            '/integrations/',
            '/test-404/',  # Allow testing custom 404 page
            '/store/',     # Exempt storefront from billing restrictions (handled by store settings)
        ]
        
        # Exact match URLs (not prefix match)
        self.exact_match_exempt = ['/']  # Landing page only

    
    def __call__(self, request):
        import logging
        logger = logging.getLogger('billing.middleware')
        
        # Log the request
        logger.debug(f"[SubscriptionMiddleware] Processing: {request.path}")
        
        # Check exact match exempt URLs first
        if request.path in self.exact_match_exempt:
            logger.debug(f"[SubscriptionMiddleware] Exact match exempt: {request.path}")
            return self.get_response(request)
        
        # Skip middleware for prefix-match exempt URLs
        if any(request.path.startswith(url) for url in self.exempt_urls):
            logger.debug(f"[SubscriptionMiddleware] Prefix exempt: {request.path}")
            return self.get_response(request)
        
        # Skip for unauthenticated users
        if not request.user.is_authenticated:
            logger.debug(f"[SubscriptionMiddleware] User not authenticated")
            return self.get_response(request)
        
        # Skip for superusers
        if request.user.is_superuser:
            logger.debug(f"[SubscriptionMiddleware] User is superuser: {request.user.username}")
            return self.get_response(request)
        
        # Check if user has a profile and it's not None
        profile = getattr(request.user, 'profile', None)
        if not profile:
            logger.debug(f"[SubscriptionMiddleware] User {request.user.username} has no profile")
            return self.get_response(request)
        
        # Check if profile has tenant
        if not profile.tenant:
            logger.debug(f"[SubscriptionMiddleware] Profile for {request.user.username} has no tenant")
            return self.get_response(request)
        
        # User has profile and tenant - check subscription
        tenant = request.user.profile.tenant
        logger.debug(f"[SubscriptionMiddleware] User: {request.user.username}, Tenant: {tenant.name} (Schema: {getattr(tenant, 'schema_name', 'N/A')})")
        
        is_active = is_subscription_active(tenant)
        logger.debug(f"[SubscriptionMiddleware] Result of is_subscription_active({tenant.name}): {is_active}")
        
        if not is_active:
            logger.warning(f"[SubscriptionMiddleware] INACTIVE subscription for tenant {tenant.name}, redirecting from {request.path}")
            
            # Allow access to branch list only if tenant has no branches yet (initial setup)
            if request.path.startswith('/accounts/branch/'):
                from accounts.models import Branch
                branch_count = Branch.objects.filter(tenant=tenant).count()
                if branch_count == 0:
                    logger.debug(f"[SubscriptionMiddleware] Allowing branch access for initial setup")
                    return self.get_response(request)
            
            # Block access to dashboard URLs for unsubscribed tenants
            if request.path.startswith('/dashboard/') or request.path.startswith('/branches/'):
                logger.warning(f"[SubscriptionMiddleware] Redirecting to subscription_required")
                return redirect('subscription_required')
            
            # Redirect to subscription required page for other protected resources
            logger.warning(f"[SubscriptionMiddleware] Redirecting to subscription_required (general)")
            return redirect('subscription_required')
        
        logger.debug(f"[SubscriptionMiddleware] Access granted for {request.path}")
        return self.get_response(request)


