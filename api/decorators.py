"""
API Security Decorators

Provides rate limiting and security decorators for API endpoints.
"""
from functools import wraps
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse


def api_ratelimit(key='ip', rate='60/m', method='ALL'):
    """
    Rate limit decorator for API endpoints.
    
    Args:
        key: What to rate limit on ('ip', 'user', 'header:x-api-key')
        rate: Rate limit (e.g., '60/m' = 60 requests per minute)
        method: HTTP methods to limit ('GET', 'POST', 'ALL')
    """
    def decorator(func):
        @wraps(func)
        @ratelimit(key=key, rate=rate, method=method, block=True)
        def wrapper(request, *args, **kwargs):
            # Check if rate limit was exceeded
            if getattr(request, 'limited', False):
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'detail': f'Too many requests. Please try again later.'
                }, status=429)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def strict_api_ratelimit(key='ip', rate='5/m', method='ALL'):
    """
    Strict rate limit for sensitive endpoints (auth, admin operations).
    
    Args:
        key: What to rate limit on
        rate: Strict rate limit (default: 5 requests per minute)
        method: HTTP methods to limit
    """
    return api_ratelimit(key=key, rate=rate, method=method)


def pos_api_ratelimit(key='user', rate='100/m', method='ALL'):
    """
    Rate limit for POS transaction endpoints.
    Higher limit to accommodate busy retail operations.
    
    Args:
        key: What to rate limit on (default: user)
        rate: Rate limit (default: 100 requests per minute)
        method: HTTP methods to limit
    """
    return api_ratelimit(key=key, rate=rate, method=method)


def webhook_ratelimit(key='ip', rate='30/m', method='POST'):
    """
    Rate limit for webhook endpoints.
    
    Args:
        key: What to rate limit on (default: IP)
        rate: Rate limit (default: 30 requests per minute)
        method: HTTP methods to limit (default: POST only)
    """
    return api_ratelimit(key=key, rate=rate, method=method)
