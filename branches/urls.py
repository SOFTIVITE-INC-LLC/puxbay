
from django.urls import path
from . import views
from . import views_loyalty
from . import views_marketing
from . import views_feedback
from . import views_inventory
from . import views_compliance
from . import views_qrcode
from . import views_stocktake
from . import views_staff
from . import views_workforce
from . import views_crm # Added views_crm as per instruction's implied import
from . import views_stocktake_portal # Added views_stocktake_portal as per instruction
from main import views_barcode, views_kanban as views_kb

urlpatterns = [
    path('stocktake/portal/<uuid:token>/', views_stocktake_portal.stocktake_portal_login, name='stocktake_portal_login'),
    path('stocktake/portal/<uuid:token>/api/scan/', views_stocktake_portal.stocktake_api_scan, name='stocktake_api_scan'),
    path('stocktake/portal/<uuid:token>/api/update/', views_stocktake_portal.stocktake_api_update, name='stocktake_api_update'),

    # Dashboard
    path('<uuid:branch_id>/dashboard/', views.dashboard, name='branch_dashboard'),
    
    # Workforce & Gamification
    path('<uuid:branch_id>/staff-portal/', views_workforce.staff_portal_view, name='staff_portal'),
    path('<uuid:branch_id>/staff-portal/swap/<uuid:shift_id>/', views_workforce.request_shift_swap, name='request_shift_swap'),
    path('<uuid:branch_id>/staff-portal/claim/<uuid:shift_id>/', views_workforce.claim_open_shift, name='claim_open_shift'),
    
    # QR Code
    path('<uuid:branch_id>/print-qr/', views_qrcode.print_qr_code, name='print_branch_qr'),
    
    # Settings
    path('<uuid:branch_id>/settings/', views.settings_view, name='settings_view'),
    
    # Category Management
    path('<uuid:branch_id>/categories/', views.category_list, name='category_list'),
    path('<uuid:branch_id>/categories/create/', views.category_create, name='category_create'),
    path('<uuid:branch_id>/categories/<uuid:pk>/', views.category_detail, name='category_detail'),
    path('<uuid:branch_id>/categories/<uuid:pk>/update/', views.category_update, name='category_update'),
    path('<uuid:branch_id>/categories/<uuid:pk>/delete/', views.category_delete, name='category_delete'),

    # Product Management
    path('<uuid:branch_id>/products/', views.product_list, name='product_list'),
    path('<uuid:branch_id>/products/create/', views.product_create, name='product_create'),
    path('<uuid:branch_id>/products/export/', views.export_products, name='export_products'),
    path('<uuid:branch_id>/products/import/', views.import_products, name='import_products'),
    path('<uuid:branch_id>/products/<uuid:pk>/', views.product_detail, name='product_detail'),
    path('<uuid:branch_id>/products/<uuid:pk>/update/', views.product_update, name='product_update'),
    path('<uuid:branch_id>/products/<uuid:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Customer Management
    path('<uuid:branch_id>/customers/', views.customer_list, name='customer_list'),
    path('<uuid:branch_id>/customers/create/', views.customer_create, name='customer_create'),
    path('<uuid:branch_id>/customers/<uuid:pk>/', views.customer_detail, name='customer_detail'),
    path('<uuid:branch_id>/customers/<uuid:pk>/update/', views.customer_update, name='customer_update'),
    path('<uuid:branch_id>/customers/<uuid:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('<uuid:branch_id>/customers/<uuid:pk>/payment/', views.record_customer_payment, name='record_customer_payment'),
    
    # Reports
    path('<uuid:branch_id>/transactions/', views.transaction_list, name='transaction_list'),
    path('<uuid:branch_id>/sales/', views.sales_list, name='sales_list'),
    path('<uuid:branch_id>/online-orders/', views.online_transaction_list, name='online_transaction_list'),
    path('<uuid:branch_id>/online-sales/', views.online_sales_list, name='online_sales_list'),
    path('<uuid:branch_id>/financial-report/', views.branch_financial_report, name='branch_financial_report'),
    path('<uuid:branch_id>/product-report/', views.branch_product_report, name='branch_product_report'),
    
    # Branch Financials (New)
    path('<uuid:branch_id>/expenses/', views.branch_expense_list, name='branch_expense_list'),
    path('<uuid:branch_id>/expenses/add/', views.branch_expense_create, name='branch_expense_create'),
    path('<uuid:branch_id>/expenses/<uuid:pk>/edit/', views.branch_expense_update, name='branch_expense_update'),
    path('<uuid:branch_id>/expenses/<uuid:pk>/delete/', views.branch_expense_delete, name='branch_expense_delete'),
    
    path('<uuid:branch_id>/reports/profit-loss/', views.branch_profit_loss_report, name='branch_profit_loss_report'),
    path('<uuid:branch_id>/reports/tax/', views.branch_tax_report, name='branch_tax_report'),
    
    # Transaction Detail
    path('<uuid:branch_id>/transactions/<uuid:order_id>/', views.transaction_detail, name='transaction_detail'),
    path('<uuid:branch_id>/transactions/<uuid:order_id>/complete/', views.complete_order, name='complete_order'),
    path('<uuid:branch_id>/transactions/<uuid:order_id>/receipt/', views.transaction_receipt, name='transaction_receipt'),
    
    # POS
    path('<uuid:branch_id>/pos/', views.pos_view, name='pos_view'),
    path('<uuid:branch_id>/pos/data/', views.pos_data_api, name='pos_data_api'),
    path('<uuid:branch_id>/pos/checkout/', views.pos_checkout, name='pos_checkout'),
    path('<uuid:branch_id>/pos/validate-pin/', views.validate_pos_pin, name='validate_pos_pin'),
    
    # Stock Transfers
    path('<uuid:branch_id>/transfers/', views.transfer_list, name='transfer_list'),
    path('<uuid:branch_id>/transfers/create/', views.transfer_create, name='transfer_create'),
    path('<uuid:branch_id>/transfers/request/', views.transfer_request, name='transfer_request'),
    path('<uuid:branch_id>/transfers/<uuid:pk>/', views.transfer_detail, name='transfer_detail'),
    path('<uuid:branch_id>/transfers/<uuid:pk>/approve/', views.transfer_approve, name='transfer_approve'),
    path('<uuid:branch_id>/transfers/<uuid:pk>/ship/', views.transfer_ship, name='transfer_ship'),
    path('<uuid:branch_id>/transfers/<uuid:pk>/receive/', views.transfer_receive, name='transfer_receive'),
    
    # Suppliers & Purchase Orders
    path('<uuid:branch_id>/suppliers/', views.supplier_list, name='supplier_list'),
    path('<uuid:branch_id>/purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('<uuid:branch_id>/purchase-orders/create/', views.purchase_order_create, name='purchase_order_create'),
    path('<uuid:branch_id>/purchase-orders/<uuid:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('<uuid:branch_id>/purchase-orders/<uuid:pk>/receive/', views.purchase_order_receive, name='purchase_order_receive'),
    
    # Alerts
    path('<uuid:branch_id>/alerts/low-stock/', views.low_stock_list, name='low_stock_list'),

    # Analytics
    path('<uuid:branch_id>/analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('<uuid:branch_id>/analytics/export-csv/', views.export_sales_csv, name='export_sales_csv'),

    # Staff Shift & Rota Management
    path('<uuid:branch_id>/shifts/', views_staff.shift_list, name='shift_list'),
    path('<uuid:branch_id>/shifts/schedule/', views_staff.schedule_shift, name='schedule_shift'),
    path('<uuid:branch_id>/shifts/<uuid:shift_id>/check-in/', views_staff.shift_check_in, name='shift_check_in'),
    path('<uuid:branch_id>/shifts/<uuid:shift_id>/check-out/', views_staff.shift_check_out, name='shift_check_out'),
    path('<uuid:branch_id>/staff-performance/<uuid:staff_id>/', views_staff.staff_performance_report, name='staff_performance_report'),
    
    # Legacy Employee Management (Optional)
    path('<uuid:branch_id>/attendance/', views.attendance_list, name='attendance_list'),
    path('<uuid:branch_id>/attendance/in/', views.clock_in, name='clock_in'),
    path('<uuid:branch_id>/attendance/out/', views.clock_out, name='clock_out'),
    path('<uuid:branch_id>/orders/<uuid:order_id>/void/', views.void_order, name='void_order'),

    # Gift Cards
    path('<uuid:branch_id>/gift-cards/', views.gift_card_list, name='gift_card_list'),
    path('<uuid:branch_id>/gift-cards/create/', views.gift_card_create, name='gift_card_create'),


    # CRM - Loyalty
    path('<uuid:branch_id>/loyalty/', views_loyalty.loyalty_dashboard, name='loyalty_dashboard'),
    path('<uuid:branch_id>/loyalty/tiers/add/', views_loyalty.tier_create, name='tier_create'),
    path('<uuid:branch_id>/loyalty/tiers/<uuid:pk>/edit/', views_loyalty.tier_update, name='tier_update'),
    path('<uuid:branch_id>/loyalty/tiers/<uuid:pk>/delete/', views_loyalty.tier_delete, name='tier_delete'),

    # CRM - Marketing
    path('<uuid:branch_id>/marketing/', views_marketing.campaign_list, name='campaign_list'),
    path('<uuid:branch_id>/marketing/create/', views_marketing.campaign_create, name='campaign_create'),
    path('<uuid:branch_id>/marketing/<uuid:pk>/edit/', views_marketing.campaign_update, name='campaign_update'),
    path('<uuid:branch_id>/marketing/<uuid:pk>/delete/', views_marketing.campaign_delete, name='campaign_delete'),
    path('<uuid:branch_id>/marketing/<uuid:pk>/send/', views_marketing.campaign_send, name='campaign_send'),

    # CRM - Feedback
    path('<uuid:branch_id>/feedback/', views_feedback.feedback_list, name='feedback_list'),

    # Inventory - Advanced
    path('<uuid:branch_id>/inventory/', views_inventory.inventory_dashboard, name='inventory_dashboard'),
    path('<uuid:branch_id>/inventory/history/', views_inventory.stock_movement_list, name='stock_movement_list'),
    path('<uuid:branch_id>/inventory/receive/', views_inventory.stock_receive, name='stock_receive'),
    path('<uuid:branch_id>/inventory/batches/', views_inventory.batch_list, name='batch_list'),
    path('<uuid:branch_id>/inventory/stocktake/', views_stocktake.stocktake_list, name='stocktake_list'),
    path('<uuid:branch_id>/inventory/stocktake/start/', views_stocktake.stocktake_start, name='stocktake_start'),
    path('<uuid:branch_id>/inventory/stocktake/<uuid:session_id>/', views_stocktake.stocktake_detail, name='stocktake_detail'),
    path('<uuid:branch_id>/inventory/stocktake/<uuid:session_id>/finalize/', views_stocktake.stocktake_finalize, name='stocktake_finalize'),
    path('<uuid:branch_id>/inventory/stocktake/<uuid:session_id>/analytics/', views_stocktake.stocktake_analytics, name='stocktake_analytics'),
    
    # Compliance & EOD
    path('<uuid:branch_id>/drawer/open/', views_compliance.open_drawer, name='open_drawer'),
    path('<uuid:branch_id>/drawer/close/', views_compliance.close_drawer, name='close_drawer'),
    path('<uuid:branch_id>/drawer/reports/<uuid:session_id>/', views_compliance.eod_report, name='eod_report'),

    # Barcodes
    path('<uuid:branch_id>/barcode/generate/<uuid:product_id>/', views_barcode.generate_product_barcode, name='generate_barcode'),
    path('<uuid:branch_id>/barcode/bulk-generate/', views_barcode.bulk_generate_barcodes_view, name='bulk_generate_barcodes'),
    
    # Kitchen Board (Kanban)
    path('<uuid:branch_id>/kanban/', views_kb.order_kanban, name='order_kanban_branch'),
    path('<uuid:branch_id>/kanban/update/', views_kb.update_order_status_api, name='update_order_status_api'),
]
