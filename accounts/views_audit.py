from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import ActivityLog

@login_required
def activity_log_list(request):
    profile = request.user.profile
    # Only allow admins or managers (if desired) to view logs
    if profile.role not in ['admin', 'manager']:
        return render(request, '403.html', status=403)
        
    logs = ActivityLog.objects.filter(tenant=profile.tenant)
    
    # Filter by user
    user_id = request.GET.get('user')
    if user_id:
        logs = logs.filter(actor__id=user_id)
        
    # Filter by action type
    action_type = request.GET.get('action')
    if action_type:
        logs = logs.filter(action_type=action_type)
        
    paginator = Paginator(logs, 50) # Show 50 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'action_types': ActivityLog.ACTION_TYPES,
        'users': profile.tenant.users.all()
    }
    return render(request, 'accounts/audit/activity_log_list.html', context)
