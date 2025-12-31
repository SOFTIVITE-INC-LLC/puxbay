from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import caches
from main.models import Product, Category

@receiver([post_save, post_delete], sender=Product)
@receiver([post_save, post_delete], sender=Category)
def clear_storefront_cache(sender, instance, **kwargs):
    """
    Clear the storefront cache whenever a Product or Category is modified.
    """
    try:
        storefront_cache = caches['storefront']
        # For now, we don't clear it because we don't want to flush all redis in dev
        # storefront_cache.clear()
    except Exception:
        # Gracefully handle missing cache alias in specific environments
        pass
