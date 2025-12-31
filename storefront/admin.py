from django.contrib import admin
from .models import (
    StorefrontSettings, ProductReview, Wishlist, 
    Coupon, NewsletterSubscription, ProductImageGallery
)

@admin.register(StorefrontSettings)
class StorefrontSettingsAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'store_name', 'is_active', 'created_at')
    search_fields = ('store_name', 'tenant__name')

@admin.register(ProductImageGallery)
class ProductImageGalleryAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_primary', 'order')
    list_filter = ('is_primary',)
    search_fields = ('product__name',)

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'rating', 'is_visible', 'created_at')
    list_filter = ('rating', 'is_visible', 'created_at')
    search_fields = ('product__name', 'customer__name', 'comment')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'created_at')
    search_fields = ('customer__name', 'product__name')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'tenant', 'discount_type', 'value', 'is_active', 'valid_to')
    list_filter = ('discount_type', 'is_active', 'valid_to')
    search_fields = ('code',)

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'tenant', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
