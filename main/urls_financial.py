"""
URL Configuration for Financial Management Features
"""
from django.urls import path
from .views_financial import (
    # Expense Management
    expense_category_list, expense_category_create, expense_category_update, expense_category_delete,
    expense_list, expense_create, expense_update, expense_delete,
    
    # Reports
    profit_loss_report,
    tax_configuration, tax_report, tax_report_export,
    
    # Payment Gateway
    payment_settings, payment_method_create, payment_method_update, 
    payment_method_delete, test_payment_connection,
    
    # Returns & Refunds
    return_list, return_create, return_detail,
    return_approve, return_reject, return_process_refund,
)

urlpatterns = [
    # Expense Categories
    path('expenses/categories/', expense_category_list, name='expense_category_list'),
    path('expenses/categories/add/', expense_category_create, name='expense_category_create'),
    path('expenses/categories/<uuid:pk>/edit/', expense_category_update, name='expense_category_update'),
    path('expenses/categories/<uuid:pk>/delete/', expense_category_delete, name='expense_category_delete'),
    
    # Expenses
    path('expenses/', expense_list, name='expense_list'),
    path('expenses/add/', expense_create, name='expense_create'),
    path('expenses/<uuid:pk>/edit/', expense_update, name='expense_update'),
    path('expenses/<uuid:pk>/delete/', expense_delete, name='expense_delete'),
    
    # Profit & Loss Report
    path('reports/profit-loss/', profit_loss_report, name='profit_loss_report'),
    
    # Tax Configuration & Reports
    path('tax/configuration/', tax_configuration, name='tax_configuration'),
    path('reports/tax/', tax_report, name='tax_report'),
    path('reports/tax/export/', tax_report_export, name='tax_report_export'),
    
    # Payment Gateway Settings
    path('payments/settings/', payment_settings, name='payment_settings'),
    path('payments/methods/add/', payment_method_create, name='payment_method_create'),
    path('payments/methods/<uuid:pk>/edit/', payment_method_update, name='payment_method_update'),
    path('payments/methods/<uuid:pk>/delete/', payment_method_delete, name='payment_method_delete'),
    path('payments/methods/<uuid:pk>/test/', test_payment_connection, name='test_payment_connection'),
    
    # Returns & Refunds
    path('returns/', return_list, name='return_list'),
    path('branches/<uuid:branch_id>/returns/', return_list, name='branch_return_list'),
    path('branches/<uuid:branch_id>/returns/add/', return_create, name='return_create'),
    path('returns/<uuid:pk>/', return_detail, name='return_detail'),
    path('branches/<uuid:branch_id>/returns/<uuid:pk>/', return_detail, name='branch_return_detail'),
    path('returns/<uuid:pk>/approve/', return_approve, name='return_approve'),
    path('returns/<uuid:pk>/reject/', return_reject, name='return_reject'),
    path('returns/<uuid:pk>/process-refund/', return_process_refund, name='return_process_refund'),
]
