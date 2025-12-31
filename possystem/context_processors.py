from django.db import connection
from accounts.models import Tenant

def tenant_context(request):
    """Add tenant information to template context"""
    context = {}
    
    # Get current schema
    schema_name = getattr(connection, 'schema_name', 'public')
    context['current_schema'] = schema_name
    
    # Get current tenant if not public
    if schema_name != 'public':
        try:
            current_tenant = Tenant.objects.get(schema_name=schema_name)
            context['current_tenant'] = current_tenant
        except Tenant.DoesNotExist:
            context['current_tenant'] = None
    else:
        context['current_tenant'] = None
    
    # Add all tenants for switcher (only for superusers)
    if request.user.is_authenticated and request.user.is_superuser:
        context['all_tenants'] = Tenant.objects.exclude(schema_name='public').order_by('name')
    else:
        context['all_tenants'] = []
    
    # Add root domain for cross-subdomain linking
    from django.conf import settings
    context['ROOT_DOMAIN'] = getattr(settings, 'ROOT_DOMAIN', 'localhost:8000')
    
    return context
