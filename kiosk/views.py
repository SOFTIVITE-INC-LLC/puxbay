from django.shortcuts import render, get_object_or_404
from accounts.models import Branch

def kiosk_index(request, branch_id):
    """
    Entry point for the Vue.js based Kiosk interface.
    """
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.tenant)
    
    context = {
        'branch': branch,
        'config': {
            'branchId': str(branch.id),
            'tenantSlug': request.tenant.schema_name,
            # Kiosk uses session auth by default for internal browser use
        }
    }
    return render(request, 'kiosk/index.html', context)
