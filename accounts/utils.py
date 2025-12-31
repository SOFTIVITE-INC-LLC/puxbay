from django.shortcuts import redirect
from functools import wraps
from .models import ActivityLog

def merchant_only(view_func):
    """
    Decorator for views that should only be accessible by standard merchants.
    Developers will be redirected to their developer dashboard.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        profile = getattr(request.user, 'profile', None)
        if profile and profile.tenant.tenant_type == 'developer':
            return redirect('developer_dashboard')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def log_activity(request, action_type, description, target_model='', target_object_id=''):
    """
    Helper function to create activity logs from views.
    """
    if not request.user.is_authenticated:
        return

    # Try to get tenant from request, or from user profile
    tenant = getattr(request, 'tenant', None)
    if not tenant and hasattr(request.user, 'profile'):
        tenant = request.user.profile.tenant
        
    if not tenant:
        # Should restrict logging if no tenant context (e.g. system admin) or handle gracefully
        return

    # Get IP Address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    ActivityLog.objects.create(
        tenant=tenant,
        actor=request.user.profile,
        action_type=action_type,
        target_model=target_model,
        target_object_id=str(target_object_id),
        description=description,
        ip_address=ip
    )
