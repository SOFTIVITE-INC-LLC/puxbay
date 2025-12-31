from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from accounts.models import CrossTenantAuditLog, Tenant

class CrossTenantAuditMiddleware(MiddlewareMixin):
    """Middleware to track when superusers access different tenants"""
    def process_request(self, request):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return None
        
        schema_name = getattr(connection, 'schema_name', 'public')
        if schema_name == 'public':
            return None
        
        try:
            # Update to handle multi-profile if needed
            from accounts.models import UserProfile
            user_profile = UserProfile.objects.filter(user=request.user).first()
            user_home_tenant = user_profile.tenant if user_profile else None
        except:
            user_home_tenant = None
            
        try:
            accessed_tenant = Tenant.objects.get(schema_name=schema_name)
        except Tenant.DoesNotExist:
            return None
            
        if user_home_tenant and accessed_tenant and user_home_tenant.id != accessed_tenant.id:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            CrossTenantAuditLog.objects.create(
                user=request.user,
                accessed_tenant=accessed_tenant,
                user_home_tenant=user_home_tenant,
                action_type='access',
                description=f"Accessed {accessed_tenant.name} admin from {user_home_tenant.name}",
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            )
        
        return None

class TenantProfileMiddleware(MiddlewareMixin):
    """
    Attaches the relevant UserProfile for the current tenant to request.user.profile
    This maintains compatibility with request.user.profile calls.
    """
    def process_request(self, request):
        if not request.user.is_authenticated:
            return None
            
        # Get schema/tenant
        schema_name = getattr(connection, 'schema_name', 'public')
        
        from accounts.models import UserProfile, Tenant
        
        # In a real django-tenants app, request.tenant is added by TenantMainMiddleware
        tenant = getattr(request, 'tenant', None)
        
        if not tenant and schema_name != 'public':
            try:
                tenant = Tenant.objects.get(schema_name=schema_name)
            except Tenant.DoesNotExist:
                pass

        if tenant:
            profile = UserProfile.objects.filter(user=request.user, tenant=tenant).first()
            if not profile:
                # Fallback to any profile if none found for this tenant (e.g. for superusers)
                profile = UserProfile.objects.filter(user=request.user).first()
            
            # Only set the profile if we found one - don't overwrite with None
            if profile:
                # Monkey patch request.user to have the correct profile for this request
                request.user.profile = profile
            
        if tenant:
            profile = UserProfile.objects.filter(user=request.user, tenant=tenant).first()
            if not profile:
                # Fallback to any profile if none found for this tenant (e.g. for superusers)
                profile = UserProfile.objects.filter(user=request.user).first()
            
            # Only set the profile if we found one - don't overwrite with None
            if profile:
                # Monkey patch request.user to have the correct profile for this request
                request.user.profile = profile
            
        return None

from django.shortcuts import redirect

class StrictAccessMiddleware(MiddlewareMixin):
    """
    Enforces strict separation between Merchant and Developer dashboards.
    Prevents cross-access even if URL is manipulated manually.
    """
    def process_request(self, request):
        if not request.user.is_authenticated:
            return None

        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return None

        path = request.path
        
        # Shared exemptions and public resources
        exempt_prefixes = [
            '/static/', '/media/', '/login/', '/logout/', '/admin/', 
            '/api/v1/intelligence/pos-recommendations/', 
            '/pricing/', '/features/', '/about/', '/contact/', '/terms/', '/privacy/', 
            '/manual/', '/sw.js', '/tinymce/', '/test-404/'
        ]
        
        if any(path.startswith(p) for p in exempt_prefixes) or path == '/':
            return None

        return None
