"""
Analytics Service for business intelligence and reporting.
Provides sales trends, revenue analysis, and performance metrics.
"""
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from datetime import timedelta, datetime
from main.models import Order, OrderItem, Product, Customer
from decimal import Decimal


def get_sales_trends(branch=None, tenant=None, period='week'):
    """
    Calculate sales trends over specified time period.
    
    Args:
        branch: Optional branch to filter by
        tenant: Tenant instance
        period: 'day', 'week', 'month', 'year'
    
    Returns:
        Dictionary with trend data and comparison
    """
    now = timezone.now()
    
    # Determine date ranges
    if period == 'day':
        current_start = now.replace(hour=0, minute=0, second=0)
        previous_start = current_start - timedelta(days=1)
        days_count = 1
    elif period == 'week':
        current_start = now - timedelta(days=7)
        previous_start = current_start - timedelta(days=7)
        days_count = 7
    elif period == 'month':
        current_start = now - timedelta(days=30)
        previous_start = current_start - timedelta(days=30)
        days_count = 30
    else:  # year
        current_start = now - timedelta(days=365)
        previous_start = current_start - timedelta(days=365)
        days_count = 365
    
    # Base query
    orders_query = Order.objects.filter(status='completed')
    if tenant:
        orders_query = orders_query.filter(tenant=tenant)
    if branch:
        orders_query = orders_query.filter(branch=branch)
    
    # Current period metrics
    current_orders = orders_query.filter(created_at__gte=current_start)
    current_revenue = current_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    current_count = current_orders.count()
    
    # Previous period metrics
    previous_orders = orders_query.filter(
        created_at__gte=previous_start,
        created_at__lt=current_start
    )
    previous_revenue = previous_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    previous_count = previous_orders.count()
    
    # Calculate growth
    revenue_growth = 0
    if previous_revenue > 0:
        revenue_growth = ((current_revenue - previous_revenue) / previous_revenue) * 100
    
    order_growth = 0
    if previous_count > 0:
        order_growth = ((current_count - previous_count) / previous_count) * 100
    
    # Daily breakdown for charts
    daily_data = []
    for i in range(days_count):
        day = current_start + timedelta(days=i)
        day_end = day + timedelta(days=1)
        
        day_orders = orders_query.filter(
            created_at__gte=day,
            created_at__lt=day_end
        )
        day_revenue = day_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        daily_data.append({
            'date': day.strftime('%Y-%m-%d'),
            'revenue': float(day_revenue),
            'orders': day_orders.count()
        })
    
    return {
        'current_revenue': float(current_revenue),
        'current_orders': current_count,
        'previous_revenue': float(previous_revenue),
        'previous_orders': previous_count,
        'revenue_growth': float(revenue_growth),
        'order_growth': float(order_growth),
        'daily_data': daily_data,
        'period': period
    }


def get_revenue_breakdown(branch=None, tenant=None, start_date=None, end_date=None):
    """
    Break down revenue by category, product, and payment method.
    
    Returns:
        Dictionary with breakdown data for charts
    """
    # Base query
    orders_query = Order.objects.filter(status='completed')
    if tenant:
        orders_query = orders_query.filter(tenant=tenant)
    if branch:
        orders_query = orders_query.filter(branch=branch)
    if start_date:
        orders_query = orders_query.filter(created_at__gte=start_date)
    if end_date:
        orders_query = orders_query.filter(created_at__lte=end_date)
    
    # Revenue by category
    items_query = OrderItem.objects.filter(order__in=orders_query)
    
    category_revenue = items_query.filter(
        product__category__isnull=False
    ).values(
        'product__category__name'
    ).annotate(
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('-revenue')
    
    # Revenue by payment method
    payment_revenue = orders_query.values('payment_method').annotate(
        revenue=Sum('total_amount'),
        count=Count('id')
    ).order_by('-revenue')
    
    # Revenue by hour (for heatmap)
    from django.db.models.functions import ExtractHour
    hourly_revenue = orders_query.annotate(
        hour=ExtractHour('created_at')
    ).values('hour').annotate(
        revenue=Sum('total_amount'),
        orders=Count('id')
    ).order_by('hour')
    
    return {
        'by_category': [
            {
                'name': item['product__category__name'],
                'revenue': float(item['revenue'])
            }
            for item in category_revenue
        ],
        'by_payment_method': [
            {
                'method': item['payment_method'],
                'revenue': float(item['revenue']),
                'count': item['count']
            }
            for item in payment_revenue
        ],
        'by_hour': [
            {
                'hour': item['hour'],
                'revenue': float(item['revenue']),
                'orders': item['orders']
            }
            for item in hourly_revenue
        ]
    }


def get_top_products(branch=None, tenant=None, limit=10, period='month'):
    """
    Get best-selling products by quantity and revenue.
    
    Returns:
        Dictionary with top products data
    """
    now = timezone.now()
    
    if period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    else:  # year
        start_date = now - timedelta(days=365)
    
    # Base query
    orders_query = Order.objects.filter(
        status='completed',
        created_at__gte=start_date
    )
    if tenant:
        orders_query = orders_query.filter(tenant=tenant)
    if branch:
        orders_query = orders_query.filter(branch=branch)
    
    items_query = OrderItem.objects.filter(order__in=orders_query)
    
    # Top by quantity
    top_by_quantity = items_query.values(
        'product__id',
        'product__name',
        'product__sku'
    ).annotate(
        quantity_sold=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('-quantity_sold')[:limit]
    
    # Top by revenue
    top_by_revenue = items_query.values(
        'product__id',
        'product__name',
        'product__sku'
    ).annotate(
        quantity_sold=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('-revenue')[:limit]
    
    return {
        'by_quantity': [
            {
                'product_id': str(item['product__id']),
                'name': item['product__name'],
                'sku': item['product__sku'],
                'quantity': item['quantity_sold'],
                'revenue': float(item['revenue'])
            }
            for item in top_by_quantity
        ],
        'by_revenue': [
            {
                'product_id': str(item['product__id']),
                'name': item['product__name'],
                'sku': item['product__sku'],
                'quantity': item['quantity_sold'],
                'revenue': float(item['revenue'])
            }
            for item in top_by_revenue
        ]
    }


def get_customer_metrics(tenant, start_date=None, end_date=None):
    """
    Calculate customer analytics and metrics.
    
    Returns:
        Dictionary with customer metrics
    """
    customers = Customer.objects.filter(tenant=tenant)
    
    # Date filtering
    orders_query = Order.objects.filter(tenant=tenant, status='completed')
    if start_date:
        orders_query = orders_query.filter(created_at__gte=start_date)
    if end_date:
        orders_query = orders_query.filter(created_at__lte=end_date)
    
    # Total customers
    total_customers = customers.count()
    
    # New vs returning
    customers_with_orders = orders_query.values('customer').distinct().count()
    
    # Customer lifetime value
    customer_clv = orders_query.values('customer').annotate(
        total_spent=Sum('total_amount'),
        order_count=Count('id')
    ).order_by('-total_spent')[:10]
    
    # Average order value
    avg_order_value = orders_query.aggregate(avg=Avg('total_amount'))['avg'] or Decimal('0')
    
    return {
        'total_customers': total_customers,
        'active_customers': customers_with_orders,
        'avg_order_value': float(avg_order_value),
        'top_customers': [
            {
                'customer_id': str(item['customer']),
                'total_spent': float(item['total_spent']),
                'order_count': item['order_count']
            }
            for item in customer_clv if item['customer']
        ]
    }


def get_real_time_metrics(branch=None, tenant=None):
    """
    Get real-time dashboard metrics.
    
    Returns:
        Dictionary with current metrics
    """
    today = timezone.now().date()
    
    # Base queries
    orders_query = Order.objects.filter(status='completed')
    if tenant:
        orders_query = orders_query.filter(tenant=tenant)
    if branch:
        orders_query = orders_query.filter(branch=branch)
    
    products_query = Product.objects.filter(is_active=True)
    if tenant:
        products_query = products_query.filter(tenant=tenant)
    if branch:
        products_query = products_query.filter(branch=branch)
    
    # Today's metrics
    today_orders = orders_query.filter(created_at__date=today)
    today_revenue = today_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    # Inventory metrics
    inventory_value = products_query.aggregate(
        value=Sum(F('stock_quantity') * F('price'))
    )['value'] or Decimal('0')
    
    low_stock_count = products_query.filter(
        stock_quantity__lte=F('low_stock_threshold'),
        stock_quantity__gt=0
    ).count()
    
    out_of_stock_count = products_query.filter(stock_quantity=0).count()
    
    return {
        'today_revenue': float(today_revenue),
        'today_orders': today_orders.count(),
        'inventory_value': float(inventory_value),
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'total_products': products_query.count()
    }


def get_heatmap_data(branch=None, tenant=None, period='month'):
    """
    Get heatmap data (Day x Hour).
    """
    from django.db.models.functions import ExtractWeekDay, ExtractHour
    
    now = timezone.now()
    if period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    elif period == 'year':
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(days=30)

    orders_query = Order.objects.filter(
        status='completed',
        created_at__gte=start_date
    )
    if tenant:
        orders_query = orders_query.filter(tenant=tenant)
    if branch:
        orders_query = orders_query.filter(branch=branch)

    # 1=Sunday, 2=Monday, ..., 7=Saturday (in Django/Postgres usually)
    heatmap_data = orders_query.annotate(
        weekday=ExtractWeekDay('created_at'),
        hour=ExtractHour('created_at')
    ).values('weekday', 'hour').annotate(
        count=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('weekday', 'hour')

    # Transform to list
    results = []
    for item in heatmap_data:
        results.append({
            'weekday': item['weekday'], # 1-7
            'hour': item['hour'],       # 0-23
            'count': item['count'],
            'revenue': float(item['revenue'])
        })
    return results
