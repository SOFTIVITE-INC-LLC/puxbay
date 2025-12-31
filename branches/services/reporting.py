from django.db.models import Sum, Count, F, Case, When, Value, DecimalField
from django.utils import timezone
from datetime import timedelta
from main.models import Order, OrderItem, Product

class ReportingService:
    def __init__(self, tenant, branch):
        self.tenant = tenant
        self.branch = branch

    def get_date_range(self, range_type, start_str=None, end_str=None):
        """
        Standardizes date range calculation across all reports.
        """
        from datetime import datetime
        now = timezone.now()
        
        if range_type == 'today':
            start = now.date()
            end = now.date()
        elif range_type == 'week':
            start = (now - timedelta(days=7)).date()
            end = now.date()
        elif range_type == 'month':
            start = (now - timedelta(days=30)).date()
            end = now.date()
        elif range_type == 'year':
            start = (now - timedelta(days=365)).date()
            end = now.date()
        elif range_type == 'all':
            start = None
            end = None
        elif range_type == 'custom' and start_str and end_str:
            try:
                start = datetime.strptime(start_str, '%Y-%m-%d').date()
                end = datetime.strptime(end_str, '%Y-%m-%d').date()
            except ValueError:
                start = (now - timedelta(days=30)).date()
                end = now.date()
        else:
            start = (now - timedelta(days=30)).date()
            end = now.date()
            
        return start, end

    def get_top_products(self, start_date, end_date, limit=10):
        """
        Calculates top selling products by quantity.
        """
        orders_query = Order.objects.filter(
            branch=self.branch, 
            status='completed',
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        items_query = OrderItem.objects.filter(order__in=orders_query)
        
        return items_query.values(
            'product__id', 'product__name', 'product__sku'
        ).annotate(
            quantity_sold=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity'))
        ).order_by('-quantity_sold')[:limit]

    def get_daily_revenue(self, start_date, end_date):
        """
        Calculates daily revenue for chart visualization.
        """
        from django.db.models.functions import TruncDay
        
        orders_query = Order.objects.filter(
            branch=self.branch, 
            status='completed',
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )

        return orders_query.annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            revenue=Sum('total_amount')
        ).order_by('day')

    def get_cashier_performance(self, start_date, end_date):
        """
        Calculates sales performance metrics for each cashier.
        """
        orders_query = Order.objects.filter(
            branch=self.branch, 
            status='completed',
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        return orders_query.values(
            'cashier__user__first_name', 'cashier__user__last_name'
        ).annotate(
            total_sales=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('-total_sales')

    def get_financial_summary(self, start_date, end_date):
        """
        Calculates key financial metrics for the branch within a date range.
        """
        orders_query = Order.objects.filter(
            branch=self.branch, 
            status='completed',
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        metrics = orders_query.aggregate(
            revenue=Sum('total_amount'),
            order_count=Count('id'),
            total_items=Sum('items__quantity')
        )
        
        total_revenue = metrics['revenue'] or 0
        total_orders = metrics['order_count'] or 0
        total_items_sold = metrics['total_items'] or 0
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Profit Calculation
        items_query = OrderItem.objects.filter(order__in=orders_query)
        total_cost = items_query.aggregate(
            cost=Sum(F('product__cost_price') * F('quantity'))
        )['cost'] or 0
        
        total_profit = total_revenue - total_cost
        profit_margin = (total_profit * 100 / total_revenue) if total_revenue > 0 else 0
        
        return {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'total_items_sold': total_items_sold,
            'avg_order_value': avg_order_value,
            'total_profit': total_profit,
            'profit_margin': profit_margin
        }

    def get_product_insights(self, start_date, end_date, limit=10):
        """
        Calculates product-related metrics: top products, margins, and stock status.
        """
        orders_query = Order.objects.filter(
            branch=self.branch, 
            status='completed',
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        items_query = OrderItem.objects.filter(order__in=orders_query)
        
        # 1. Top Products
        top_products = items_query.values(
            'product__name', 'product__sku'
        ).annotate(
            quantity_sold=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity'))
        ).order_by('-quantity_sold')[:limit]
        
        # 2. Best Sellers
        best_sellers = items_query.values(
            'product__id', 'product__name', 'product__sku'
        ).annotate(
            quantity_sold=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity'))
        ).order_by('-quantity_sold')[:limit]
        
        # 3. Worst Performers
        worst_performers = items_query.values(
            'product__id', 'product__name', 'product__sku'
        ).annotate(
            quantity_sold=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity'))
        ).order_by('quantity_sold')[:limit]

        # 4. Product Margins
        product_margins = items_query.values(
            'product__id', 'product__name', 'product__sku'
        ).annotate(
            revenue=Sum(F('price') * F('quantity')),
            cost=Sum(F('product__cost_price') * F('quantity'))
        ).annotate(
            profit=F('revenue') - F('cost'),
            margin_percent=Case(
                When(revenue__gt=0, then=(F('profit') * 100.0 / F('revenue'))),
                default=Value(0),
                output_field=DecimalField()
            )
        ).order_by('-profit')[:limit]
        
        # 5. Stock Status
        all_products = Product.objects.filter(branch=self.branch, is_active=True)
        inventory_value = all_products.aggregate(
            total_value=Sum(F('stock_quantity') * F('price'))
        )['total_value'] or 0
        
        low_stock_items = all_products.filter(
            stock_quantity__lte=F('low_stock_threshold'),
            stock_quantity__gt=0
        ).values('id', 'name', 'sku', 'stock_quantity', 'low_stock_threshold', 'price')[:limit]
        
        out_of_stock_items = all_products.filter(stock_quantity=0).values('id', 'name', 'sku', 'price')[:limit]
        out_of_stock_count = all_products.filter(stock_quantity=0).count()
        
        return {
            'top_products': top_products,
            'best_sellers': best_sellers,
            'worst_performers': worst_performers,
            'product_margins': product_margins,
            'inventory_value': inventory_value,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'out_of_stock_count': out_of_stock_count
        }

    def get_company_financial_summary(self, start_date, end_date):
        """
        Calculates aggregate financial metrics across all branches for the tenant.
        """
        orders_query = Order.objects.filter(
            tenant=self.tenant,
            status='completed',
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        metrics = orders_query.aggregate(
            revenue=Sum('total_amount'),
            order_count=Count('id')
        )
        
        total_revenue = metrics['revenue'] or 0
        total_orders = metrics['order_count'] or 0
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Profit Calculation (Aggregate across all branches for tenant)
        items_query = OrderItem.objects.filter(order__in=orders_query)
        total_cost = items_query.aggregate(
            cost=Sum(F('product__cost_price') * F('quantity'))
        )['cost'] or 0
        total_profit = total_revenue - total_cost
        profit_margin = (total_profit * 100 / total_revenue) if total_revenue > 0 else 0
        
        # Branch-wise breakdown
        branch_performance = Order.objects.filter(
            tenant=self.tenant,
            status='completed',
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).values('branch__id', 'branch__name').annotate(
            revenue=Sum('total_amount'),
            orders=Count('id')
        ).order_by('-revenue')
        
        return {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'avg_order_value': avg_order_value,
            'total_profit': total_profit,
            'profit_margin': profit_margin,
            'branch_performance': branch_performance
        }

    def get_company_stock_insights(self, limit=10):
        """
        Calculates aggregate inventory metrics across all company branches.
        """
        all_products = Product.objects.filter(tenant=self.tenant, is_active=True)
        
        inventory_value = all_products.aggregate(
            total_value=Sum(F('stock_quantity') * F('price'))
        )['total_value'] or 0
        
        low_stock_count = all_products.filter(
            stock_quantity__lte=F('low_stock_threshold'),
            stock_quantity__gt=0
        ).count()
        
        out_of_stock_count = all_products.filter(stock_quantity=0).count()
        
        # Company-wide product margins
        items_query = OrderItem.objects.filter(order__tenant=self.tenant, order__status='completed')
        product_margins = items_query.values(
            'product__id', 'product__name', 'product__sku'
        ).annotate(
            revenue=Sum(F('price') * F('quantity')),
            cost=Sum(F('product__cost_price') * F('quantity')),
            quantity_sold=Sum('quantity')
        ).annotate(
            profit=F('revenue') - F('cost'),
            margin_percent=Case(
                When(revenue__gt=0, then=(F('profit') * 100.0 / F('revenue'))),
                default=Value(0),
                output_field=DecimalField()
            )
        ).order_by('-profit')[:limit]
        
        return {
            'company_inventory_value': inventory_value,
            'company_low_stock_count': low_stock_count,
            'company_out_of_stock': out_of_stock_count,
            'product_margins_company': product_margins
        }

    def get_company_top_products(self, start_date, end_date, limit=10):
        """
        Calculates top selling products across all company branches.
        """
        orders_query = Order.objects.filter(
            tenant=self.tenant,
            status='completed',
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        items_query = OrderItem.objects.filter(order__in=orders_query)
        
        return items_query.values(
            'product__id', 'product__name', 'product__sku'
        ).annotate(
            revenue=Sum(F('price') * F('quantity')),
            quantity_sold=Sum('quantity')
        ).order_by('-revenue')[:limit]

    def get_company_revenue_by_category(self, start_date, end_date):
        """
        Calculates revenue breakdown by category across all branches.
        """
        orders_query = Order.objects.filter(
            tenant=self.tenant,
            status='completed',
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        items_query = OrderItem.objects.filter(order__in=orders_query)
        
        return items_query.filter(
            product__category__isnull=False
        ).values(
            'product__category__name'
        ).annotate(
            revenue=Sum(F('price') * F('quantity')),
            quantity_sold=Sum('quantity')
        ).order_by('-revenue')

    def get_revenue_by_category(self, start_date, end_date):
        """
        Calculates revenue breakdown by product category.
        """
        orders_query = Order.objects.filter(
            branch=self.branch, 
            status='completed',
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        items_query = OrderItem.objects.filter(order__in=orders_query)
        
        return items_query.filter(
            product__category__isnull=False
        ).values(
            'product__category__id', 'product__category__name'
        ).annotate(
            revenue=Sum(F('price') * F('quantity')),
            quantity_sold=Sum('quantity')
        ).order_by('-revenue')
