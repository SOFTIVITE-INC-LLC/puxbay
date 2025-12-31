from functools import wraps
from django.shortcuts import render, get_object_or_404
from .models import StorefrontSettings
from accounts.models import Tenant

def storefront_active_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, tenant_slug, branch_id, *args, **kwargs):
        # Prefer request.tenant if it matches the slug
        tenant = getattr(request, 'tenant', None)
        if not tenant or (tenant.subdomain != tenant_slug):
            tenant = get_object_or_404(Tenant, subdomain=tenant_slug)
        
        store_settings = StorefrontSettings.objects.filter(tenant=tenant).first()
        
        # Determine if the user is an admin for this tenant
        is_admin = False
        if request.user.is_authenticated:
            try:
                # Use the profile attached by middleware if possible, else fetch
                profile = getattr(request.user, 'profile', None)
                if not profile or profile.tenant != tenant:
                    from accounts.models import UserProfile
                    profile = UserProfile.objects.filter(user=request.user, tenant=tenant).first()
                
                is_admin = profile and profile.role == 'admin'
            except:
                pass

        # If store is inactive (or missing) and user is NOT an admin, show inactive page
        # Note: if store_settings is None, we treat as inactive (default behavior)
        if (not store_settings or not store_settings.is_active) and not is_admin:
            from accounts.models import Branch
            branch = get_object_or_404(Branch, id=branch_id, tenant=tenant)
            return render(request, 'storefront/inactive.html', {
                'tenant': tenant,
                'branch': branch,
                'store_settings': store_settings
            })
            
        return view_func(request, tenant_slug, branch_id, *args, **kwargs)
    return _wrapped_view
