from django.urls import path
from . import views
from .views_pwa import storefront_manifest
urlpatterns = [
    path('<slug:tenant_slug>/<uuid:branch_id>/', views.store_home, name='store_home'),
    path('<slug:tenant_slug>/<uuid:branch_id>/cart/', views.store_cart, name='store_cart'),
    path('<slug:tenant_slug>/<uuid:branch_id>/cart/add/<uuid:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('<slug:tenant_slug>/<uuid:branch_id>/cart/update/<uuid:product_id>/', views.update_cart, name='update_cart'),
    path('<slug:tenant_slug>/<uuid:branch_id>/cart/remove/<uuid:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('<slug:tenant_slug>/<uuid:branch_id>/checkout/', views.store_checkout, name='store_checkout'),
    path('<slug:tenant_slug>/<uuid:branch_id>/order/<uuid:order_id>/success/', views.store_order_success, name='store_order_success'),
    path('<slug:tenant_slug>/<uuid:branch_id>/product/<uuid:product_id>/', views.product_detail, name='product_detail'),
    path('<slug:tenant_slug>/<uuid:branch_id>/api/search/', views.api_search, name='api_search'),

    # Authentication
    path('<slug:tenant_slug>/<uuid:branch_id>/login/', views.customer_login, name='customer_login'),
    path('<slug:tenant_slug>/<uuid:branch_id>/register/', views.customer_register, name='customer_register'),
    path('<slug:tenant_slug>/<uuid:branch_id>/verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('<slug:tenant_slug>/<uuid:branch_id>/logout/', views.customer_logout, name='customer_logout'),
    path('<slug:tenant_slug>/<uuid:branch_id>/account/orders/', views.customer_orders, name='customer_orders'),
    path('<slug:tenant_slug>/<uuid:branch_id>/account/profile/', views.customer_profile, name='customer_profile'),
    path('<slug:tenant_slug>/<uuid:branch_id>/account/wishlist/', views.customer_wishlist, name='customer_wishlist'),
    path('<slug:tenant_slug>/<uuid:branch_id>/wishlist/toggle/<uuid:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('<slug:tenant_slug>/<uuid:branch_id>/review/submit/<uuid:product_id>/', views.submit_review, name='submit_review'),
    path('<slug:tenant_slug>/<uuid:branch_id>/coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('<slug:tenant_slug>/<uuid:branch_id>/coupon/remove/', views.remove_coupon, name='remove_coupon'),
    path('<slug:tenant_slug>/<uuid:branch_id>/newsletter/subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('<slug:tenant_slug>/<uuid:branch_id>/track-order/', views.track_order, name='track_order'),
    
    # Abandoned Cart Recovery
    path('recover-cart/<uuid:cart_id>/', views.recover_cart, name='recover_cart'),
    
    # PWA Manifest
    path('<slug:tenant_slug>/<uuid:branch_id>/manifest.json', storefront_manifest, name='storefront_manifest'),
    
    # Footer Pages
    path('<slug:tenant_slug>/<uuid:branch_id>/about/', views.store_about, name='store_about'),
    path('<slug:tenant_slug>/<uuid:branch_id>/privacy/', views.store_privacy, name='store_privacy'),
    path('<slug:tenant_slug>/<uuid:branch_id>/terms/', views.store_terms, name='store_terms'),
    path('<slug:tenant_slug>/<uuid:branch_id>/contact/', views.store_contact, name='store_contact'),
    path('<slug:tenant_slug>/<uuid:branch_id>/shipping/', views.store_shipping, name='store_shipping'),
    path('<slug:tenant_slug>/<uuid:branch_id>/returns/', views.store_returns, name='store_returns'),
    
    # Management URL
    # Since this is "Admin" dashboard context, it shouldn't conflict with public store URLs.
    # However, store urls start with <slug>. If we put 'settings/' it might clash if slug is 'settings'.
    # Better to put this in 'accounts/urls.py' or 'main/urls.py'?
    # Or make it 'manage/store-settings/'
    path('manage/settings/', views.update_store_settings, name='update_store_settings'),
]
