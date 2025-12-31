from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import connection
from django.utils import timezone
import shutil
import os
from .models import UserProfile
from notifications.utils import send_notification

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'admin'

from accounts.utils import merchant_only

@login_required
@merchant_only
@user_passes_test(is_admin)
def system_health_dashboard(request):
    """
    Displays system health status: Database, Disk Usage, etc.
    """
    context = {}
    
    # Check Database
    try:
        connection.ensure_connection()
        context['db_status'] = 'Online'
        context['db_color'] = 'text-green-600'
    except Exception as e:
        context['db_status'] = f'Error: {str(e)}'
        context['db_color'] = 'text-red-600'
        
    # Check Disk Usage (Root path)
    total, used, free = shutil.disk_usage("/")
    context['disk_total'] = f"{total // (2**30)} GB"
    context['disk_used'] = f"{used // (2**30)} GB"
    context['disk_free'] = f"{free // (2**30)} GB"
    context['disk_percent'] = (used / total) * 100
    
    # Critical Alert Logic (Simulated trigger on visit for demonstration)
    if (free / total) < 0.1: # Less than 10% free
         context['disk_color'] = 'text-red-600'
         # Throttle this in real app
         send_notification(
             user=request.user,
             title="Critical System Alert: Low Disk Space",
             message=f"Server disk space is critical. Only {context['disk_free']} remaining.",
             level='error',
             category='system'
         )
    else:
        context['disk_color'] = 'text-green-600'

    return render(request, 'accounts/system/health.html', context)
