from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from accounts.models import Tenant
from .models import StorefrontSettings

def storefront_manifest(request, tenant_slug, branch_id):
    """Generate a dynamic PWA manifest for the storefront with tenant branding."""
    tenant = get_object_or_404(Tenant, subdomain=tenant_slug)
    store_settings = StorefrontSettings.objects.filter(tenant=tenant).first()
    
    manifest = {
        "name": store_settings.store_name if store_settings else tenant.name,
        "short_name": (store_settings.store_name if store_settings else tenant.name)[:12],
        "description": f"Professional online shopping experience at {store_settings.store_name if store_settings else tenant.name}",
        "start_url": f"/store/{tenant_slug}/{branch_id}/",
        "scope": f"/store/{tenant_slug}/{branch_id}/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": store_settings.primary_color if store_settings else "#3b82f6",
        "orientation": "portrait-primary",
        "icons": [
            {
                "src": store_settings.logo_image.url if store_settings and store_settings.logo_image else "/static/pwa/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any"
            },
            {
                "src": store_settings.logo_image.url if store_settings and store_settings.logo_image else "/static/pwa/icon-192-maskable.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "maskable"
            },
            {
                "src": store_settings.logo_image.url if store_settings and store_settings.logo_image else "/static/pwa/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any"
            }
        ],
        "screenshots": [
            {
                "src": "/static/pwa/screenshots/home.png",
                "sizes": "1080x1920",
                "type": "image/png",
                "form_factor": "narrow",
                "label": "Home Screen"
            },
            {
                "src": "/static/pwa/screenshots/product.png",
                "sizes": "1080x1920",
                "type": "image/png",
                "form_factor": "narrow",
                "label": "Product View"
            }
        ],
        "shortcuts": [
            {
                "name": "Cart",
                "url": f"/store/{tenant_slug}/{branch_id}/cart/",
                "icons": [{"src": "/static/pwa/icons/cart.png", "sizes": "96x96"}]
            },
            {
                "name": "My Orders",
                "url": f"/store/{tenant_slug}/{branch_id}/account/orders/",
                "icons": [{"src": "/static/pwa/icons/orders.png", "sizes": "96x96"}]
            }
        ],
        "categories": ["shopping", "business"],
        "prefer_related_applications": False
    }
    
    return JsonResponse(manifest, content_type='application/manifest+json')
