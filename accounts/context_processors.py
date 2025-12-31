from django.db import connection
from .models import SEOSettings, Tenant

def seo_settings(request):
    """
    Injects global SEO settings into templates.
    """
    seo = None
    if hasattr(request, 'tenant'):
        try:
            seo = SEOSettings.objects.get(tenant=request.tenant)
        except SEOSettings.DoesNotExist:
            pass
            
    if seo:
        return {'seo_settings': seo}
    
    return {
        'seo_settings': {
            'meta_title': None,
            'meta_description': None,
            'keywords': None,
            'og_title': None,
            'og_description': None,
            'og_image': None,
            'google_analytics_id': None,
            'facebook_pixel_id': None,
            'homepage_video_id': 'dQw4w9WgXcQ',
        }
    }

def api_key_processor(request):
    """
    Injects the tenant's POS API key into the template context.
    Used for PWA/Service Worker authentication.
    """
    if hasattr(request, 'tenant') and request.tenant:
        return {'pos_api_key': request.tenant.pos_api_key}
    return {'pos_api_key': None}
