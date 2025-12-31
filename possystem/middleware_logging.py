"""
Correlation ID middleware for request tracking.
"""
import uuid
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class CorrelationIDMiddleware(MiddlewareMixin):
    """
    Middleware to add correlation IDs to requests for distributed tracing.
    
    Checks for existing correlation ID in headers, otherwise generates a new one.
    Adds correlation ID to response headers and logging context.
    """
    
    CORRELATION_ID_HEADER = 'X-Correlation-ID'
    
    def process_request(self, request):
        """Add correlation ID to request."""
        # Check if correlation ID exists in headers
        correlation_id = request.META.get(f'HTTP_{self.CORRELATION_ID_HEADER.upper().replace("-", "_")}')
        
        if not correlation_id:
            # Generate new correlation ID
            correlation_id = str(uuid.uuid4())
        
        # Store in request
        request.correlation_id = correlation_id
        
        # Add to logging context
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                'correlation_id': correlation_id,
                'method': request.method,
                'path': request.path,
                'user_id': str(request.user.id) if request.user.is_authenticated else None,
            }
        )
        
        return None
    
    def process_response(self, request, response):
        """Add correlation ID to response headers."""
        if hasattr(request, 'correlation_id'):
            response[self.CORRELATION_ID_HEADER] = request.correlation_id
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.path} - {response.status_code}",
                extra={
                    'correlation_id': request.correlation_id,
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                }
            )
        
        return response
