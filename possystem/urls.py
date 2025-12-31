"""
URL configuration for possystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import register_tenant, branch_list, branch_create, branch_update, staff_list, staff_create, staff_update, staff_delete, logout_view, verification_sent, activate_account, user_profile
from main.views import landing, dashboard, features, about, contact, integrations, company_financial_report, company_product_report, test_404, user_manual, offline_view, set_currency, terms_of_service, privacy_policy, refund_policy, cookie_policy, blog_home, blog_detail, blog_category, submit_feedback
from main.views_sw import service_worker
from main.views_health import health_check, readiness_check, metrics_check
from billing.views import pricing_view
from branches.views_feedback import public_feedback_submit
from accounts.views_security import setup_2fa, verify_2fa, disable_2fa
from accounts.views_audit import activity_log_list
from accounts.views_privacy import privacy_dashboard, export_customer_data, anonymize_customer
from accounts.views_backup import backup_dashboard, restore_backup
from accounts.views_system import system_health_dashboard
from main.views_company import company_marketing_list, company_campaign_create, company_feedback_list, company_attendance_list
from main import views_analytics as views_ana
from main import views_command as views_cmd
from main import views_portal as views_portal
from main import views_kanban as views_kb
from main import views_intelligence as views_intel
from main import views_exports
from main import views_barcode, views_analytics, views_supplier, views_workforce, views_supplier_portal
from billing.views_populate import populate_plans_view
from main.sitemaps import StaticViewSitemap, BlogSitemap
from django.contrib.sitemaps.views import sitemap
from main.views import robots_txt

sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogSitemap,
}


urlpatterns = [
    # Health Check Endpoints (for monitoring and load balancers)
    path('health/', health_check, name='health_check'),
    path('health/ready/', readiness_check, name='readiness_check'),
    path('health/metrics/', metrics_check, name='metrics_check'),
    
    path('landing/', landing, name='landing_alias'),
    path('admin/', admin.site.urls),
    path('set-currency/', set_currency, name='set_currency'),
    path('submit-feedback/', submit_feedback, name='submit_feedback'),
    
    # Supplier Portal
    path('supplier-portal/', views_supplier_portal.supplier_dashboard, name='supplier_dashboard'),
    path('supplier-portal/pos/', views_supplier_portal.supplier_po_list, name='supplier_po_list'),
    path('supplier-portal/pos/<uuid:po_id>/', views_supplier_portal.supplier_po_detail, name='supplier_po_detail'),
    path('supplier-portal/pos/<uuid:po_id>/accept/', views_supplier_portal.supplier_po_accept, name='supplier_po_accept'),
    path('supplier-portal/credit/', views_supplier_portal.supplier_credit_history, name='supplier_credit_history'),
    path('supplier-portal/payment/<uuid:transaction_id>/confirm/', views_supplier_portal.supplier_confirm_payment, name='supplier_confirm_payment'),
    
    # Commission Rules
    path('dashboard/workforce/commissions/', views_workforce.commission_rule_list, name='commission_rule_list'),
    path('dashboard/workforce/commissions/create/', views_workforce.commission_rule_create, name='commission_rule_create'),
    path('dashboard/workforce/commissions/<uuid:pk>/delete/', views_workforce.commission_rule_delete, name='commission_rule_delete'),
    
    # Kanban Board
    path('dashboard/kanban/', views_kb.order_kanban_redirect, name='order_kanban'),

    # Supplier Management
    path('dashboard/suppliers/', views_supplier.supplier_list, name='supplier_list'),
    path('dashboard/suppliers/create/', views_supplier.supplier_create, name='supplier_create'),
    path('dashboard/suppliers/<uuid:supplier_id>/', views_supplier.supplier_detail, name='supplier_detail'),
    path('dashboard/suppliers/<uuid:supplier_id>/edit/', views_supplier.supplier_update, name='supplier_update'),
    path('dashboard/suppliers/<uuid:supplier_id>/delete/', views_supplier.supplier_delete, name='supplier_delete'),
    path('dashboard/suppliers/<uuid:supplier_id>/share/', views_supplier.supplier_share_access, name='supplier_share_access'),
    path('dashboard/suppliers/<uuid:supplier_id>/payment/', views_supplier.record_supplier_payment, name='record_supplier_payment'),

    # Intelligence & Analytics
    path('intelligence/inventory/', views_intel.inventory_forecast_view, name='inventory_forecast'),
    path('intelligence/inventory/<uuid:branch_id>/', views_intel.inventory_forecast_view, name='inventory_forecast_branch'),
    path('intelligence/auto-po/', views_intel.generate_auto_pos_api, name='generate_auto_pos'),
    path('intelligence/auto-po/branch/<uuid:branch_id>/', views_intel.generate_auto_pos_api, name='generate_auto_pos_branch'),
    path('api/v1/intelligence/pos-recommendations/', views_intel.get_pos_recommendations, name='pos_recommendations'),
    path('intelligence/staff/', views_intel.staff_leaderboard_view, name='staff_leaderboard'),
    path('intelligence/staff/<uuid:branch_id>/', views_intel.staff_leaderboard_view, name='staff_leaderboard_branch'),

    # Analytics URLs
    path('analytics/', views_analytics.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/<uuid:branch_id>/', views_analytics.analytics_dashboard, name='analytics_dashboard_branch'),
    path('analytics/api/sales-trends/', views_analytics.sales_trends_api, name='sales_trends_api'),
    path('analytics/api/revenue-breakdown/', views_analytics.revenue_breakdown_api, name='revenue_breakdown_api'),
    path('analytics/api/top-products/', views_analytics.top_products_api, name='top_products_api'),
    path('analytics/api/customer-metrics/', views_analytics.customer_metrics_api, name='customer_metrics_api'),

    # Export URLs
    path('export/sales/<uuid:branch_id>/', views_exports.export_sales, name='export_sales'),
    path('export/inventory/<uuid:branch_id>/', views_exports.export_inventory, name='export_inventory'),
    path('export/customers/', views_exports.export_customers, name='export_customers'),
    path('export/order-items/<uuid:branch_id>/', views_exports.export_order_items, name='export_order_items'),

    # Barcode URLs
    path('barcode/image/<uuid:product_id>/', views_barcode.barcode_image, name='barcode_image'),
    path('barcode/print/<uuid:product_id>/', views_barcode.print_barcode_label, name='print_barcode'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        html_email_template_name='emails/password_reset_email.html'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    
    path('signup/', register_tenant, name='signup'),
    path('signup/verification-sent/', verification_sent, name='verification_sent'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate_account'),
    
    # Security
    path('security/2fa/setup/', setup_2fa, name='setup_2fa'),
    path('security/2fa/verify/', verify_2fa, name='verify_2fa'),
    path('security/2fa/disable/', disable_2fa, name='disable_2fa'),
    path('security/audit/', activity_log_list, name='activity_log_list'),
    path('security/privacy/', privacy_dashboard, name='privacy_dashboard'),
    path('security/privacy/export/<uuid:customer_id>/', export_customer_data, name='export_customer_data'),
    path('security/privacy/anonymize/<uuid:customer_id>/', anonymize_customer, name='anonymize_customer'),
    path('security/backup/', backup_dashboard, name='backup_dashboard'),
    path('security/backup/restore/', restore_backup, name='restore_backup'),
    path('security/system-health/', system_health_dashboard, name='system_health_dashboard'),
    
    # Developer Console (Removed)
    
    
    
    # Advanced Analytics
    path('dashboard/analytics/heatmap/', views_ana.sales_heatmap, name='sales_heatmap'),
    path('dashboard/analytics/heatmap/api/', views_ana.heatmap_api, name='heatmap_api'),
    path('dashboard/analytics/heatmap/api/<uuid:branch_id>/', views_ana.heatmap_api, name='heatmap_api_branch'),
    path('dashboard/analytics/report-builder/', views_ana.custom_report_builder, name='report_builder'),
    path('dashboard/analytics/report-builder/data/', views_ana.custom_report_data, name='report_builder_data'),
    
    # Enterprise Command Center
    path('dashboard/enterprise/command-center/', views_cmd.command_center, name='command_center'),
    path('dashboard/enterprise/price-sync/', views_cmd.global_price_update, name='global_price_sync'),
    
    # Public Customer Portal
    path('customer-portal/', views_portal.customer_portal_login, name='customer_portal_login'),
    path('customer-portal/<uuid:tenant_id>/', views_portal.public_customer_portal, name='public_customer_portal'),
    
    # Staff Management (Admin Only)
    path('staff/', staff_list, name='staff_list'),
    path('staff/add/', staff_create, name='staff_create'),
    path('staff/<uuid:pk>/', staff_update, name='staff_update'),
    path('staff/<uuid:pk>/delete/', staff_delete, name='staff_delete'),
    path('profile/', user_profile, name='user_profile'),
    
    # Branch Management
    path('branches/', branch_list, name='branch_list'),
    path('branches/add/', branch_create, name='branch_create'),
    path('branches/<uuid:pk>/', branch_update, name='branch_update'),
    path('billing/', include('billing.urls')),
    path('branches/', include('branches.urls')),
    path('notifications/', include('notifications.urls')),
    path('financial/', include('main.urls_financial')),  # Financial management features
    path('store/', include('storefront.urls')), # Public Storefront
    path('kiosk/', include('kiosk.urls')), # Kiosk Mode
    path('wallet/', include('wallet.urls')), # MyWallet PWA
    
    # Product Management
    # Moved to branches/urls.py

    path('dashboard/', dashboard, name='dashboard'),
    path('reports/financial/', company_financial_report, name='company_financial_report'),
    path('reports/products/', company_product_report, name='company_product_report'),
    path('marketing/', company_marketing_list, name='company_marketing_list'),
    path('marketing/create/', company_campaign_create, name='company_campaign_create'),
    path('feedback/', company_feedback_list, name='company_feedback_list'),
    path('attendance/', company_attendance_list, name='company_attendance_list'),
    path('pricing/', pricing_view, name='pricing'),
    path('features/', features, name='features'),
    path('manual/', user_manual, name='user_manual'),
    path('integrations/', integrations, name='integrations'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('feedback/<uuid:tenant_id>/', public_feedback_submit, name='public_feedback_submit'),
    path('test-404/', test_404, name='test_404'),  # Test view for custom 404 page
    path('terms/', terms_of_service, name='terms_of_service'),
    path('privacy/', privacy_policy, name='privacy_policy'),
    path('refund-policy/', refund_policy, name='refund_policy'),
    path('cookies/', cookie_policy, name='cookie_policy'),
    
    # Blog
    path('blog/', blog_home, name='blog_home'),
    path('blog/category/<slug:slug>/', blog_category, name='blog_category'),
    path('blog/<slug:slug>/', blog_detail, name='blog_detail'),
    path('offline/', offline_view, name='offline'),
    path('sw.js', service_worker, name='service_worker'),
    path('populate-plans/', populate_plans_view, name='populate_plans'),
    path('tinymce/', include('tinymce.urls')),
    
    # API URLs
    path('api/v1/', include('api.urls')),
    
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
    
    path('', landing, name='landing'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers (used when DEBUG=False)
handler404 = 'possystem.error_handlers.custom_404'
handler500 = 'possystem.error_handlers.custom_500'

