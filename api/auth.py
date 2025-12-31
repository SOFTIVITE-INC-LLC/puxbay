import hashlib
import redis
from django.conf import settings
from django.utils import timezone
from rest_framework import authentication, exceptions
from accounts.models import APIKey
import logging
logger = logging.getLogger(__name__)

class APIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        api_key_header = request.META.get('HTTP_X_API_KEY')
        if not api_key_header:
            return None

        # Format: pb_xyz123...
        if not api_key_header.startswith('pb_') or len(api_key_header) < 15:
            raise exceptions.AuthenticationFailed('Invalid API key format')

        prefix = api_key_header[:8]
        key_hash = hashlib.sha256(api_key_header.encode()).hexdigest()

        try:
            key_obj = APIKey.objects.select_related('tenant', 'tenant__subscription', 'tenant__subscription__plan').get(
                key_prefix=prefix,
                key_hash=key_hash,
                is_active=True
            )
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid or inactive API key')

        # 1. Check Subscription Plan (skip for internal POS keys)
        tenant = key_obj.tenant
        
        # Internal POS keys (name="Internal POS Key") bypass subscription checks
        is_internal_key = key_obj.name == "Internal POS Key"
        
        if not is_internal_key:
            subscription = getattr(tenant, 'subscription', None)
            
            if not subscription or subscription.status not in ['active', 'trialing']:
                raise exceptions.AuthenticationFailed('Active subscription required for API access')

            plan = subscription.plan
            if not plan or not plan.api_access:
                raise exceptions.AuthenticationFailed(f'Your current plan ({plan.name if plan else "N/A"}) does not include API access')

            # 2. Daily Quota Enforcement (Redis) - only for non-internal keys
            self.check_quota(tenant, plan.api_daily_limit)

        # Update last used
        # We use a threshold to avoid constant DB writes
        # (This is a simplified version)
        key_obj.last_used_at = timezone.now()
        key_obj.save(update_fields=['last_used_at'])

        # Return (User, Auth)
        # Note: API keys are linked to Tenants, but for DRF we need a user object.
        # We'll return the tenant's primary admin or a placeholder.
        admin_user = tenant.users.filter(role='admin').first()
        user = admin_user.user if admin_user else None
        
        if user and admin_user:
            # Manually attach profile to match middleware behavior for consistency
            user.profile = admin_user
        
        # 3. Sandbox Isolation Enforcement
        # Prevent using Sandbox keys on Production and vice-versa
        if key_obj.is_sandbox != tenant.is_sandbox:
            env_type = "Sandbox" if tenant.is_sandbox else "Production"
            key_type = "Sandbox" if key_obj.is_sandbox else "Production"
            raise exceptions.AuthenticationFailed(
                f"Environment Mismatch: Cannot use a {key_type} key on a {env_type} environment."
            )

        # 4. Subdomain Enforcement
        # Ensure the request is coming through the tenant's specific subdomain
        host = request.get_host().split(':')[0].lower() # Remove port if present
        
        # In a real multi-tenant production environment with django-tenants,
        # request.tenant should already be set by the middleware based on the hostname.
        # However, we double-check here to strictly enforce that the key matches the domain.
        if tenant.subdomain.lower() != 'public':
            # Construct expected domain (handling development localhost too)
            expected_subdomain = tenant.subdomain.lower()
            
            # If we are not on the correct subdomain, reject the request
            # This handles cases where a developer might try to use a key on the main domain or another tenant's domain
            if not host.startswith(f"{expected_subdomain}."):
                # If host is exactly the subdomain (e.g. in some local setups)
                if host != expected_subdomain:
                     raise exceptions.AuthenticationFailed(
                         f"Strict Subdomain Enforcement: This API key is only valid for '{expected_subdomain}' subdomain."
                     )

        # Attach tenant and branch to request for convenience
        request.tenant = tenant
        request.branch = key_obj.branch
        
        return (user, api_key_header)

    def check_quota(self, tenant, daily_limit):
        if not settings.REDIS_URL:
            return  # Skip if Redis not configured

        r = redis.from_url(settings.REDIS_URL)
        now = timezone.now().timestamp()
        
        # 1. Daily Sliding Window (24 hours)
        daily_key = f"api_sliding_daily:{tenant.id}"
        daily_window = 86400  # 24 hours
        
        # 2. Minute Burst Window (60 seconds)
        minute_key = f"api_sliding_minute:{tenant.id}"
        minute_window = 60
        minute_limit = 60 # 60 requests per minute burst limit

        try:
            pipe = r.pipeline()
            # Clean up old entries
            pipe.zremrangebyscore(daily_key, 0, now - daily_window)
            pipe.zremrangebyscore(minute_key, 0, now - minute_window)
            
            # Get current counts
            pipe.zcard(daily_key)
            pipe.zcard(minute_key)
            
            results = pipe.execute()
            daily_count = results[2]
            minute_count = results[3]

            if minute_count >= minute_limit:
                 raise exceptions.PermissionDenied('Burst rate limit exceeded (60 req/min)')

            if daily_count >= daily_limit:
                raise exceptions.PermissionDenied('Daily API quota exceeded (Sliding 24h)')

            # Add current request
            pipe.zadd(daily_key, {str(now): now})
            pipe.zadd(minute_key, {str(now): now})
            pipe.expire(daily_key, daily_window + 60)
            pipe.expire(minute_key, minute_window + 60)
            pipe.execute()

        except redis.RedisError:
            pass  # Fallback to allow if Redis is down

from rest_framework import permissions

class RequireAPIKey(permissions.BasePermission):
    """
    Permission class that requires a valid API Key to be present.
    It checks if the authentication method used was APIKeyAuthentication.
    """
    def has_permission(self, request, view):
        # Allow OPTIONS requests for CORS
        if request.method == 'OPTIONS':
            return True
        
        # Check if the request was authenticated via APIKeyAuthentication
        # When APIKeyAuthentication succeeds, it sets request.auth to the raw key
        # and request.user to the tenant's admin.
        # We can also check for the custom 'tenant' attribute we added.
        return bool(request.user and hasattr(request, 'tenant'))

def require_api_key_django(view_func):
    """
    Decorator for plain Django views to enforce API key authentication.
    """
    from django.http import JsonResponse
    from functools import wraps

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # logger.warning(f"VIEW AUTH: Path={request.path} Method={request.method} User={request.user} Auth={request.user.is_authenticated if request.user else False}...")
        # Fallback to Session Authentication if already logged in via web UI
        # BUT only if the profile is correctly attached (middleware success)
        if request.user and request.user.is_authenticated and hasattr(request.user, 'profile'):
            return view_func(request, *args, **kwargs)

        api_key = request.headers.get('X-API-Key') or request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
             return JsonResponse({'error': 'X-API-Key header is required'}, status=401)

        # Standard Format: pb_xyz123...
        if not api_key.startswith('pb_') or len(api_key) < 15:
            return JsonResponse({'error': 'Invalid API key format'}, status=401)
        
        from accounts.models import APIKey
        import hashlib
        
        try:
            prefix = api_key[:8]
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            key_obj = APIKey.objects.select_related('tenant').get(
                key_prefix=prefix, 
                key_hash=key_hash, 
                is_active=True
            )
            
            request.tenant = key_obj.tenant
            
            # Subdomain Enforcement for plain Django views
            host = request.get_host().split(':')[0].lower()
            if key_obj.tenant.subdomain.lower() != 'public':
                expected = key_obj.tenant.subdomain.lower()
                if not host.startswith(f"{expected}.") and host != expected:
                    return JsonResponse({
                        'error': f"Strict Subdomain Enforcement: This API key is only valid for '{expected}' subdomain."
                    }, status=403)

            # Assign user context
            # CRITICAL: Never overwrite request.user if already authenticated
            # This prevents session loss when API calls are made during an active session
            if request.user and request.user.is_authenticated:
                # User is already authenticated via session
                # Just ensure they have a profile for this tenant
                if not hasattr(request.user, 'profile'):
                    profile = key_obj.tenant.users.filter(user=request.user).first()
                    if profile:
                        request.user.profile = profile
                    else:
                        # User is authenticated but has no profile in this tenant
                        # This is okay for API calls - we'll use a fallback for the request context
                        # but we MUST NOT modify request.user to preserve the session
                        profile = key_obj.tenant.users.filter(role='admin').first()
                        if profile:
                            # Store in a separate attribute to avoid session conflicts
                            request.api_user_profile = profile
                        else:
                            return JsonResponse({'error': 'Configuration Error: No valid profile found for this tenant.'}, status=401)
            else:
                # Not authenticated via session - use API key to determine user
                # This is safe because there's no session to preserve
                profile = key_obj.tenant.users.filter(role='admin').first()
                if profile:
                    request.user = profile.user
                    request.user.profile = profile
                else:
                    return JsonResponse({'error': 'Configuration Error: No valid profile found for this tenant.'}, status=401)
                
            return view_func(request, *args, **kwargs)
        except APIKey.DoesNotExist:
            return JsonResponse({'error': 'Invalid or inactive API key'}, status=401)
        
        except Exception as e:
            logger.exception(f"Unexpected error in require_api_key_django: {str(e)}")
            return JsonResponse({'error': f'Authentication error: {str(e)}'}, status=500)
            
    return _wrapped_view
