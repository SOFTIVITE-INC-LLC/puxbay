from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag(takes_context=True)
def get_tenant_dashboard_url(context):
    try:
        request = context['request']
        user = request.user
        
        if not user.is_authenticated:
            return "/login/" # Fallback
            
        if not hasattr(user, 'profile') or not user.profile.tenant:
            return "/dashboard/" # No tenant, standard dashboard
            
        tenant_subdomain = user.profile.tenant.subdomain
        
        # Get current host
        host = request.get_host()
        scheme = request.scheme
        
        # Logic to replace/add subdomain
        host_parts = host.split(':')
        domain = host_parts[0]
        port = host_parts[1] if len(host_parts) > 1 else None

        domain_parts = domain.split('.')
        
        # Determine base domain
        if len(domain_parts) > 2: # e.g. sub.domain.com -> domain.com
             base_domain = '.'.join(domain_parts[1:])
        elif len(domain_parts) == 2 and domain_parts[1] == 'localhost': # sub.localhost -> localhost
             base_domain = 'localhost'
        else: # domain.com or localhost
             base_domain = domain

        # Construct new host
        new_host = f"{tenant_subdomain}.{base_domain}"
        if port:
            new_host = f"{new_host}:{port}"
        
        return f"{scheme}://{new_host}/dashboard/"
        
    except Exception as e:
        return "/dashboard/" # Fail safe

@register.filter
def subtract(value, arg):
    try:
        return value - arg
    except (ValueError, TypeError):
        return value

@register.filter
def replace_str(value, args):
    if not value: return ""
    search, replace = args.split(',')
    return value.replace(search, replace)
