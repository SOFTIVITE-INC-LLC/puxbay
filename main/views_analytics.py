"""
Analytics views for dashboard and API endpoints.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import Branch
from main.services.analytics_service import (
    get_sales_trends,
    get_revenue_breakdown,
    get_top_products,
    get_customer_metrics,
    get_real_time_metrics
)


from accounts.utils import merchant_only

@login_required
@merchant_only
def analytics_dashboard(request, branch_id=None):
    """
    Main analytics dashboard with comprehensive business intelligence.
    Accessible to admin and manager roles.
    """
    profile = request.user.profile
    tenant = profile.tenant
    
    # Permission check
    if profile.role not in ['admin', 'manager', 'financial']:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You don't have permission to access analytics.")
    
    # Get branch or use tenant-wide
    branch = None
    if branch_id:
        branch = get_object_or_404(Branch, id=branch_id, tenant=tenant)
    
    # Get period from query params
    period = request.GET.get('period', 'week')
    
    # Fetch analytics data
    sales_trends = get_sales_trends(branch=branch, tenant=tenant, period=period)
    revenue_breakdown = get_revenue_breakdown(branch=branch, tenant=tenant)
    top_products = get_top_products(branch=branch, tenant=tenant, limit=10, period=period)
    customer_metrics = get_customer_metrics(tenant=tenant)
    real_time = get_real_time_metrics(branch=branch, tenant=tenant)
    
    # Get all branches for selector
    branches = Branch.objects.filter(tenant=tenant)
    
    context = {
        'branch': branch,
        'branches': branches,
        'period': period,
        'sales_trends': sales_trends,
        'revenue_breakdown': revenue_breakdown,
        'top_products': top_products,
        'customer_metrics': customer_metrics,
        'real_time': real_time,
        'title': 'Analytics Dashboard'
    }
    
    return render(request, 'main/analytics/dashboard.html', context)


@login_required
@merchant_only
def sales_trends_api(request, branch_id=None):
    """
    API endpoint for sales trend data.
    Returns JSON for AJAX chart updates.
    """
    profile = request.user.profile
    if profile.role not in ['admin', 'manager', 'financial']:
        return JsonResponse({'error': 'Permission denied'}, status=403)
        
    tenant = profile.tenant
    
    # Get branch
    branch = None
    if branch_id:
        branch = get_object_or_404(Branch, id=branch_id, tenant=tenant)
    
    # Get period
    period = request.GET.get('period', 'week')
    
    # Get data
    data = get_sales_trends(branch=branch, tenant=tenant, period=period)
    
    return JsonResponse(data)


@login_required
@merchant_only
def revenue_breakdown_api(request, branch_id=None):
    """
    API endpoint for revenue breakdown data.
    Returns JSON for pie/bar charts.
    """
    profile = request.user.profile
    if profile.role not in ['admin', 'manager', 'financial']:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    tenant = profile.tenant
    
    # Get branch
    branch = None
    if branch_id:
        branch = get_object_or_404(Branch, id=branch_id, tenant=tenant)
    
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Get data
    data = get_revenue_breakdown(
        branch=branch,
        tenant=tenant,
        start_date=start_date,
        end_date=end_date
    )
    
    return JsonResponse(data)


@login_required
@merchant_only
def top_products_api(request, branch_id=None):
    """
    API endpoint for top products data.
    Returns JSON for tables and charts.
    """
    profile = request.user.profile
    if profile.role not in ['admin', 'manager', 'financial']:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    tenant = profile.tenant
    
    # Get branch
    branch = None
    if branch_id:
        branch = get_object_or_404(Branch, id=branch_id, tenant=tenant)
    
    # Get parameters
    limit = int(request.GET.get('limit', 10))
    period = request.GET.get('period', 'month')
    
    # Get data
    data = get_top_products(
        branch=branch,
        tenant=tenant,
        limit=limit,
        period=period
    )
    
    return JsonResponse(data)


@login_required
@merchant_only
def customer_metrics_api(request):
    """
    API endpoint for customer metrics.
    Returns JSON for customer analytics.
    """
    profile = request.user.profile
    if profile.role not in ['admin', 'manager', 'financial']:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    tenant = profile.tenant
    
    # Get date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Get data
    data = get_customer_metrics(
        tenant=tenant,
        start_date=start_date,
        end_date=end_date
    )
    
    
    return JsonResponse(data)


@login_required
@merchant_only
def sales_heatmap(request):
    """
    View for the sales heatmap visualization.
    """
    profile = request.user.profile
    tenant = profile.tenant
    
    # Permission check
    if profile.role not in ['admin', 'manager', 'financial']:
        from django.shortcuts import redirect
        return redirect('dashboard')
        
    # Get all branches
    branches = Branch.objects.filter(tenant=tenant)
    
    context = {
        'branches': branches,
        'title': 'Sales Heatmap'
    }
    return render(request, 'main/analytics/sales_heatmap.html', context)


@login_required
@merchant_only
def custom_report_builder(request):
    """
    View for the custom report builder interface.
    """
    profile = request.user.profile
    tenant = profile.tenant
    
    # Permission check
    if profile.role not in ['admin', 'financial']:
        from django.shortcuts import redirect
        return redirect('dashboard')
        
    context = {
        'title': 'Report Builder'
    }
    return render(request, 'main/analytics/report_builder.html', context)


@login_required
@merchant_only
def custom_report_data(request):
    """
    API endpoint for generating custom report data.
    """
    profile = request.user.profile
    if profile.role not in ['admin', 'financial']:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    tenant = profile.tenant
    
    metric = request.GET.get('metric', 'revenue')
    period = request.GET.get('period', 'month')
    groupby = request.GET.get('groupby', 'day')
    
    from datetime import timedelta
    from django.db.models import Sum, Count, Avg
    from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
    from main.models import Order, OrderItem
    
    # Determine date range
    now = timezone.now()
    if period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    else:  # year
        start_date = now - timedelta(days=365)
    
    # Base query
    orders = Order.objects.filter(
        tenant=tenant,
        status='completed',
        created_at__gte=start_date
    )
    
    labels = []
    values = []
    
    # Group by logic
    if groupby == 'day':
        data = orders.annotate(date=TruncDay('created_at')).values('date')
    elif groupby == 'week':
        data = orders.annotate(date=TruncWeek('created_at')).values('date')
    elif groupby == 'month':
        data = orders.annotate(date=TruncMonth('created_at')).values('date')
    elif groupby == 'category':
        items = OrderItem.objects.filter(order__in=orders, product__category__isnull=False)
        data = items.values('product__category__name')
    elif groupby == 'payment':
        data = orders.values('payment_method')
    else:
        data = orders.annotate(date=TruncDay('created_at')).values('date')
    
    # Metric calculation
    if metric == 'revenue':
        if groupby in ['category']:
            data = data.annotate(value=Sum('price') * Sum('quantity'))
        else:
            data = data.annotate(value=Sum('total_amount'))
    elif metric == 'orders':
        data = data.annotate(value=Count('id'))
    elif metric == 'avg_order':
        data = data.annotate(value=Avg('total_amount'))
    elif metric == 'customers':
        data = data.annotate(value=Count('customer', distinct=True))
    elif metric == 'products_sold':
        if groupby in ['day', 'week', 'month']:
            items = OrderItem.objects.filter(order__in=orders)
            if groupby == 'day':
                data = items.annotate(date=TruncDay('order__created_at')).values('date').annotate(value=Sum('quantity'))
            elif groupby == 'week':
                data = items.annotate(date=TruncWeek('order__created_at')).values('date').annotate(value=Sum('quantity'))
            else:
                data = items.annotate(date=TruncMonth('order__created_at')).values('date').annotate(value=Sum('quantity'))
        else:
            items = OrderItem.objects.filter(order__in=orders)
            if groupby == 'category':
                data = items.filter(product__category__isnull=False).values('product__category__name').annotate(value=Sum('quantity'))
            else:
                data = items.values('order__payment_method').annotate(value=Sum('quantity'))
    
    # Extract labels and values
    for item in data:
        if groupby in ['day', 'week', 'month']:
            labels.append(item['date'].strftime('%Y-%m-%d'))
        elif groupby == 'category':
            labels.append(item.get('product__category__name', 'Uncategorized'))
        elif groupby == 'payment':
            labels.append(item.get('payment_method', 'Unknown'))
        
        values.append(float(item.get('value', 0)))
    
    return JsonResponse({
        'labels': labels,
        'values': values
    })

@login_required
def heatmap_api(request, branch_id=None):
    """
    API endpoint for heatmap data.
    """
    profile = request.user.profile
    if profile.role not in ['admin', 'manager', 'financial']:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    tenant = profile.tenant
    
    # Get branch
    branch = None
    if branch_id:
        branch = get_object_or_404(Branch, id=branch_id, tenant=tenant)
        
    period = request.GET.get('period', 'month')
    
    from main.services.analytics_service import get_heatmap_data
    data = get_heatmap_data(branch=branch, tenant=tenant, period=period)
    
    return JsonResponse({'data': data})
