from django import template
from main.models import Product
from django.db.models import F

register = template.Library()

@register.inclusion_tag('main/widgets/inventory_forecast.html', takes_context=True)
def inventory_forecast_widget(context, count=5):
    """
    Renders a list of products predicted to run out of stock soon.
    """
    request = context['request']
    if hasattr(request.user, 'profile'):
        tenant = request.user.profile.tenant
        
        # Get all active products with stock > 0
        # We can't easily filter by a method in DB, so we have to fetch candidates
        # Optimization: Filter low stock candidates first or fetch all (if dataset is small < 1000)
        # For scalability, we should cache this or have a cron job update a 'days_remaining' field.
        # For now, we'll fetch active products and sort in python (MVP).
        
        products = Product.objects.filter(
            tenant=tenant, 
            is_active=True, 
            stock_quantity__gt=0
        )
        
        forecasts = []
        for p in products:
            days = p.get_days_until_stockout()
            if days < 30: # Only care if running out this month
                forecasts.append({
                    'product': p,
                    'days_left': days,
                    'velocity': p.get_daily_sales_velocity()
                })
        
        # Sort by days left ascending (soonest to run out first)
        forecasts.sort(key=lambda x: x['days_left'])
        
        return {
            'forecasts': forecasts[:count]
        }
    return {'forecasts': []}

@register.inclusion_tag('main/widgets/staff_leaderboard.html', takes_context=True)
def staff_leaderboard_widget(context, days=30):
    """
    Renders Top Performing Staff
    """
    request = context['request']
    if hasattr(request.user, 'profile'):
        tenant = request.user.profile.tenant
        from main.models import Order
        from django.db.models import Sum, Count
        from django.utils import timezone
        import datetime
        
        start_date = timezone.now() - datetime.timedelta(days=days)
        
        # Aggregate stats by cashier
        # We need to filter by completed orders
        
        leaderboard = Order.objects.filter(
            tenant=tenant,
            status='completed',
            created_at__gte=start_date,
            cashier__isnull=False
        ).values('cashier__user__first_name', 'cashier__user__last_name', 'cashier__user__username') \
         .annotate(
             total_sales=Sum('total_amount'),
             orders_count=Count('id')
         ).order_by('-total_sales')[:5]
         
        return {
            'leaderboard': leaderboard,
            'days': days
        }
    return {'leaderboard': []}
