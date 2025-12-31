import io
import json
from django.core.management import call_command
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .utils import log_activity

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'admin'

from .utils import log_activity, merchant_only

@login_required
@merchant_only
@user_passes_test(is_admin)
def backup_dashboard(request):
    """View to initiate backup"""
    if request.method == 'POST':
        # Create backup
        buf = io.StringIO()
        # Dump critical apps
        call_command('dumpdata', 'accounts', 'branches', 'main', stdout=buf)
        buf.seek(0)
        
        timestamp = timezone.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"backup_{request.user.profile.tenant.subdomain}_{timestamp}.json"
        
        response = HttpResponse(buf.read(), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        log_activity(request, 'backup', f"Downloaded system backup", 'System', '')
        
        return response
        
    return render(request, 'accounts/backup/dashboard.html')

@login_required
@merchant_only
@user_passes_test(is_admin)
def restore_backup(request):
    """View to restore backup from uploaded file"""
    if request.method == 'POST' and request.FILES.get('backup_file'):
        import tempfile
        import os
        from django.contrib import messages
        from django.shortcuts import redirect
        
        backup_file = request.FILES['backup_file']
        
        # Validation
        if not backup_file.name.endswith('.json'):
            messages.error(request, "Invalid file format. Please upload a JSON file.")
            return redirect('backup_dashboard')

        try:
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
                for chunk in backup_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name
                
            # Call loaddata
            call_command('loaddata', tmp_path)
            
            # Clean up
            os.remove(tmp_path)
            
            log_activity(request, 'backup', "Restored system from backup file", 'System', '')
            messages.success(request, "System successfully restored from backup.")
            
        except Exception as e:
            messages.error(request, f"Restore failed: {str(e)}")
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                 os.remove(tmp_path)
                 
    return redirect('backup_dashboard')
