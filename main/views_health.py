"""
Health check views for monitoring and load balancers.
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import time


def health_check(request):
    """
    Basic liveness check.
    Returns 200 if the application is running.
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'POS System',
        'timestamp': time.time()
    })


def readiness_check(request):
    """
    Readiness check for load balancers.
    Verifies database and cache connectivity.
    """
    checks = {
        'database': False,
        'cache': False,
    }
    
    # Check database connection
    try:
        connection.ensure_connection()
        checks['database'] = True
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'checks': checks,
            'error': f'Database connection failed: {str(e)}'
        }, status=503)
    
    # Check Redis cache
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            checks['cache'] = True
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'checks': checks,
            'error': f'Cache connection failed: {str(e)}'
        }, status=503)
    
    # All checks passed
    if all(checks.values()):
        return JsonResponse({
            'status': 'ready',
            'checks': checks,
            'timestamp': time.time()
        })
    else:
        return JsonResponse({
            'status': 'unhealthy',
            'checks': checks
        }, status=503)


def metrics_check(request):
    """
    System metrics endpoint (optional).
    Returns basic system information.
    """
    from django.db import connections
    
    # Get database info
    db_info = {}
    for db_name in connections:
        try:
            conn = connections[db_name]
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_info[db_name] = 'connected'
        except Exception as e:
            db_info[db_name] = f'error: {str(e)}'
    
    return JsonResponse({
        'status': 'ok',
        'metrics': {
            'databases': db_info,
            'debug_mode': settings.DEBUG,
            'environment': getattr(settings, 'SENTRY_ENVIRONMENT', 'unknown'),
        },
        'timestamp': time.time()
    })
