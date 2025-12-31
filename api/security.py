"""
API Security Utilities

Provides IP whitelisting, signature validation, and other security utilities.
"""
import hmac
import hashlib
import ipaddress
from functools import wraps
from django.http import JsonResponse
from django.conf import settings
from typing import List, Optional


def get_client_ip(request) -> str:
    """
    Get the client's IP address from the request.
    Handles X-Forwarded-For header for proxied requests.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_ip_whitelisted(ip: str, whitelist: Optional[List[str]] = None) -> bool:
    """
    Check if an IP address is in the whitelist.
    Supports both individual IPs and CIDR notation.
    
    Args:
        ip: IP address to check
        whitelist: List of whitelisted IPs/CIDR ranges (defaults to settings.WHITELISTED_IPS)
    
    Returns:
        True if IP is whitelisted or whitelist is empty, False otherwise
    """
    if whitelist is None:
        whitelist = getattr(settings, 'WHITELISTED_IPS', [])
    
    # If no whitelist configured, allow all
    if not whitelist:
        return True
    
    try:
        client_ip = ipaddress.ip_address(ip)
        
        for allowed in whitelist:
            # Check if it's a network range (CIDR)
            if '/' in allowed:
                if client_ip in ipaddress.ip_network(allowed, strict=False):
                    return True
            # Check if it's an exact IP match
            elif client_ip == ipaddress.ip_address(allowed):
                return True
        
        return False
    except ValueError:
        # Invalid IP address
        return False


def require_ip_whitelist(func):
    """
    Decorator to restrict access to whitelisted IPs only.
    Apply to sensitive endpoints like admin operations or data exports.
    
    Usage:
        @require_ip_whitelist
        def sensitive_view(request):
            ...
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        client_ip = get_client_ip(request)
        
        if not is_ip_whitelisted(client_ip):
            return JsonResponse({
                'error': 'Access denied',
                'detail': 'Your IP address is not authorized to access this endpoint.'
            }, status=403)
        
        return func(request, *args, **kwargs)
    return wrapper


def generate_webhook_signature(payload: bytes, secret: str) -> str:
    """
    Generate HMAC-SHA256 signature for webhook payload.
    
    Args:
        payload: Webhook payload as bytes
        secret: Webhook secret key
    
    Returns:
        Hex-encoded signature
    """
    return hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify webhook signature.
    
    Args:
        payload: Webhook payload as bytes
        signature: Signature to verify
        secret: Webhook secret key
    
    Returns:
        True if signature is valid, False otherwise
    """
    expected_signature = generate_webhook_signature(payload, secret)
    return hmac.compare_digest(signature, expected_signature)


def require_webhook_signature(secret_key: str = 'WEBHOOK_SECRET'):
    """
    Decorator to validate webhook signatures.
    
    Args:
        secret_key: Settings key name for webhook secret (default: 'WEBHOOK_SECRET')
    
    Usage:
        @require_webhook_signature()
        def webhook_handler(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Get signature from header
            signature = request.META.get('HTTP_X_WEBHOOK_SIGNATURE')
            
            if not signature:
                return JsonResponse({
                    'error': 'Missing signature',
                    'detail': 'X-Webhook-Signature header is required.'
                }, status=401)
            
            # Get secret from settings
            secret = getattr(settings, secret_key, None)
            if not secret:
                # If no secret configured, log warning but allow (for development)
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'{secret_key} not configured - webhook signature validation skipped')
                return func(request, *args, **kwargs)
            
            # Verify signature
            payload = request.body
            if not verify_webhook_signature(payload, signature, secret):
                return JsonResponse({
                    'error': 'Invalid signature',
                    'detail': 'Webhook signature verification failed.'
                }, status=401)
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
