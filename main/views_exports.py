"""
Export views for generating downloadable reports.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from accounts.models import Branch
from main.models import Order, Product, Customer, OrderItem
from main.services.exports import (
    export_sales_report,
    export_inventory_report,
    export_customer_report,
    export_order_items_report
)
from datetime import datetime, timedelta


@login_required
def export_sales(request, branch_id):
    """Export sales report for a specific branch."""
    branch = get_object_or_404(Branch, id=branch_id, tenant=request.user.profile.tenant)
    
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    format_type = request.GET.get('format', 'csv')
    
    # Default to last 30 days if no dates provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Filter orders
    orders = Order.objects.filter(
        branch=branch,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).select_related('customer', 'branch').order_by('-created_at')
    
    return export_sales_report(orders, format=format_type)


@login_required
def export_inventory(request, branch_id):
    """Export inventory report for a specific branch."""
    branch = get_object_or_404(Branch, id=branch_id, tenant=request.user.profile.tenant)
    format_type = request.GET.get('format', 'csv')
    
    # Filter products
    products = Product.objects.filter(
        branch=branch,
        is_active=True
    ).select_related('category', 'branch').order_by('name')
    
    return export_inventory_report(products, format=format_type)


@login_required
def export_customers(request):
    """Export customer report for the tenant."""
    tenant = request.user.profile.tenant
    format_type = request.GET.get('format', 'csv')
    
    # Get all customers for the tenant
    customers = Customer.objects.filter(
        tenant=tenant
    ).order_by('-created_at')
    
    return export_customer_report(customers, format=format_type)


@login_required
def export_order_items(request, branch_id):
    """Export detailed order items report."""
    branch = get_object_or_404(Branch, id=branch_id, tenant=request.user.profile.tenant)
    
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    format_type = request.GET.get('format', 'csv')
    
    # Default to last 30 days if no dates provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Filter order items
    order_items = OrderItem.objects.filter(
        order__branch=branch,
        order__created_at__date__gte=start_date,
        order__created_at__date__lte=end_date
    ).select_related('order', 'product').order_by('-order__created_at')
    
    return export_order_items_report(order_items, format=format_type)
