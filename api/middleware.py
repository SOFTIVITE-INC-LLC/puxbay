"""
API Middleware
"""
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import logging
logger = logging.getLogger(__name__)
import time


class APIRateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware for API endpoints
    """
    def process_request(self, request):
        if request.path.startswith('/api/'):
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Rate limit: 100 requests per minute
            cache_key = f'api_rate_limit_{ip}'
            requests = cache.get(cache_key, [])
            now = time.time()
            
            # Remove requests older than 1 minute
            requests = [req_time for req_time in requests if now - req_time < 60]
            
            if len(requests) >= 100:
                return JsonResponse({
                    'error': 'Rate limit exceeded. Please try again later.'
                }, status=429)
            
            requests.append(now)
            cache.set(cache_key, requests, 60)
        
        return None


class APIKeyCsrfExemptMiddleware(MiddlewareMixin):
    """
    Middleware to exempt requests with valid API keys from CSRF validation.
    This prevents Django from modifying sessions during API calls.
    """
    
    def process_request(self, request):
        # Check if request has a valid API key header
        api_key = request.headers.get('X-API-Key') or request.META.get('HTTP_X_API_KEY')
        
        if api_key and api_key.startswith('pb_'):
            # Mark this request as CSRF exempt
            setattr(request, '_dont_enforce_csrf_checks', True)
        
        return None

    def process_response(self, request, response):
        if hasattr(response, 'cookies') and response.cookies:
             # Only log if sessionid is being modified
             for k, v in response.cookies.items():
                 if k == 'sessionid':
                     logger.warning(f"COOKIE MODIFIED: {k}={v}")
        return response

class APISubdomainMiddleware(MiddlewareMixin):
    """
    Middleware to route requests from api.* and developer-type tenants
    to the dedicated API URL configuration.
    """
    def process_request(self, request):
        host = request.get_host().split(':')[0].lower()
        parts = host.split('.')
        
        if parts[0] == 'manual':
            request.urlconf = 'documentation.urls_manual'
            return None
        
        return None


class APIAuditMiddleware(MiddlewareMixin):
    """
    Middleware to log all API requests for security auditing and compliance.
    
    Logs:
    - Request metadata (endpoint, method, user, IP)
    - Request/response bodies (encrypted)
    - Response time and status code
    """
    
    # Endpoints to exclude from logging (health checks, static files, etc.)
    EXCLUDED_PATHS = [
        '/health/',
        '/ready/',
        '/static/',
        '/media/',
        '/admin/jsi18n/',
    ]
    
    # Maximum body size to log (in bytes) - prevent logging huge payloads
    MAX_BODY_SIZE = 10000  # 10KB
    
    def process_request(self, request):
        """Mark the start time of the request"""
        request._api_audit_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log the API request after response is generated"""
        
        # Only log API requests
        if not request.path.startswith('/api/'):
            return response
        
        # Skip excluded paths
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return response
        
        # Skip if audit logging is disabled
        from django.conf import settings
        if not getattr(settings, 'ENABLE_API_AUDIT_LOGGING', True):
            return response
        
        try:
            # Calculate response time
            start_time = getattr(request, '_api_audit_start_time', None)
            if start_time:
                response_time_ms = int((time.time() - start_time) * 1000)
            else:
                response_time_ms = 0
            
            # Get tenant from request
            tenant = getattr(request, 'tenant', None)
            
            # Get user (may be None for unauthenticated requests)
            user = request.user if request.user.is_authenticated else None
            
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR', '')
            
            # Get request body (limit size)
            request_body = {}
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    body = request.body
                    if len(body) <= self.MAX_BODY_SIZE:
                        request_body = body.decode('utf-8')
                    else:
                        request_body = f"[Body too large: {len(body)} bytes]"
                except Exception:
                    request_body = "[Unable to decode body]"
            
            # Get response body (limit size)
            response_body = {}
            if hasattr(response, 'content'):
                try:
                    content = response.content
                    if len(content) <= self.MAX_BODY_SIZE:
                        response_body = content.decode('utf-8')
                    else:
                        response_body = f"[Body too large: {len(content)} bytes]"
                except Exception:
                    response_body = "[Unable to decode body]"
            
            # Create log entry asynchronously to avoid blocking the response
            self._create_log_entry(
                tenant=tenant,
                user=user,
                endpoint=request.path,
                method=request.method,
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                request_body=request_body,
                status_code=response.status_code,
                response_body=response_body,
                response_time_ms=response_time_ms
            )
        
        except Exception as e:
            # Log the error but don't break the response
            logger.error(f"Failed to log API request: {str(e)}")
        
        return response
    
    def _create_log_entry(self, **kwargs):
        """
        Create the log entry in the database.
        In production, this should be done asynchronously (e.g., via Celery).
        """
        try:
            from accounts.models import APIRequestLog
            APIRequestLog.objects.create(**kwargs)
        except Exception as e:
            logger.error(f"Failed to create API log entry: {str(e)}")
