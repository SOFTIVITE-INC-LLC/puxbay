"""
Middleware to handle database replica failover.

Automatically falls back to primary if replica is unavailable.
"""
from django.db import connections
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class ReplicaHealthCheckMiddleware:
    """
    Middleware to check replica health and disable if unavailable.
    """
    
    CACHE_KEY = 'db_replica_available'
    CACHE_TIMEOUT = 60  # Check every 60 seconds
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check replica health before processing request
        self.check_replica_health()
        
        response = self.get_response(request)
        return response
    
    def check_replica_health(self):
        """
        Check if replica database is available.
        Cache the result to avoid checking on every request.
        """
        # Check cache first
        cached_status = cache.get(self.CACHE_KEY)
        if cached_status is not None:
            return cached_status
        
        # Test replica connection
        try:
            conn = connections['replica']
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            # Replica is available
            cache.set(self.CACHE_KEY, True, self.CACHE_TIMEOUT)
            return True
            
        except Exception as e:
            logger.warning(f"Replica database unavailable: {e}")
            cache.set(self.CACHE_KEY, False, self.CACHE_TIMEOUT)
            
            # Temporarily disable replica by using primary
            connections['replica'] = connections['default']
            return False
