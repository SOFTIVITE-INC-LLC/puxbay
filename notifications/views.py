from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Notification

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context['unread_count'] = qs.filter(is_read=False).count()
        context['critical_count'] = qs.filter(notification_type='error').count()
        context['total_count'] = qs.count()
        
        # Preserve branch context if coming from branch dashboard
        if hasattr(self.request.user, 'profile') and self.request.user.profile.branch:
            context['branch'] = self.request.user.profile.branch
        
        return context

@login_required
@require_POST
def mark_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)

@login_required
@require_POST
def mark_all_as_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})
@login_required
def get_latest_notifications(request):
    """
    API endpoint for real-time notification polling.
    Returns JSON with unread count and latest 5 unread messages.
    """
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    
    # Get latest 5 unread notifications
    latest = Notification.objects.filter(
        recipient=request.user, 
        is_read=False
    )[:5]
    
    data = []
    from django.utils.timesince import timesince
    
    for note in latest:
        data.append({
            'id': str(note.id),
            'message': note.message,
            'link': note.link,
            'created_at_display': f"{timesince(note.created_at)} ago"
        })
        
    return JsonResponse({
        'count': unread_count,
        'notifications': data
    })
