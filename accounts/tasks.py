from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db import connection
from .models import ActivityLog, AuditLog, APIRequestLog
import logging

logger = logging.getLogger(__name__)

@shared_task
def prune_old_logs(days=90):
    """
    Deletes log entries older than the specified number of days.
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    
    # Prune ActivityLog
    activity_count, _ = ActivityLog.objects.filter(timestamp__lt=cutoff_date).delete()
    
    # Prune AuditLog
    audit_count, _ = AuditLog.objects.filter(timestamp__lt=cutoff_date).delete()
    
    # Prune APIRequestLog
    api_count, _ = APIRequestLog.objects.filter(timestamp__lt=cutoff_date).delete()
    
    logger.info(f"Pruned old logs: {activity_count} Activity, {audit_count} Audit, {api_count} API logs deleted.")
    
    # Optional: Run VACUUM or similar if using PostgreSQL and many rows were deleted
    # with connection.cursor() as cursor:
    #     cursor.execute("VACUUM ANALYZE accounts_activitylog;")
    
    return {
        'activity_pruned': activity_count,
        'audit_pruned': audit_count,
        'api_pruned': api_count
    }
