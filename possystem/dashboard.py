from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from datetime import timedelta
from main.models import Order, Product, Customer

def dashboard_callback(request, context):
    """
    Callback function to provide data for the Unfold admin dashboard.
    Enhanced with subscription revenue, API usage, and tenant analytics.
    """
    import sys
    print("=" * 80, file=sys.stderr)
    print("DASHBOARD CALLBACK TRIGGERED!", file=sys.stderr)
    print(f"Request path: {request.path}", file=sys.stderr)
    print(f"Context keys: {context.keys()}", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    
    from django.db import connection
    
    # Safe schema check
    schema_name = getattr(connection, 'schema_name', 'public')
    print(f"Schema: {schema_name}", file=sys.stderr)
        
    # =========================================================================
    # PUBLIC SCHEMA - Platform-wide Admin Dashboard
    # =========================================================================
    if schema_name == 'public':
        from accounts.models import Tenant, APIKey
        from billing.models import Subscription, Plan
        from accounts.models import WebhookEvent
        
        now = timezone.now()
        days_ago_30 = now - timedelta(days=30)
        days_ago_7 = now - timedelta(days=7)
        
        # ---------------------------------------------------------------------
        # Subscription Revenue Metrics
        # ---------------------------------------------------------------------
        active_subscriptions = Subscription.objects.filter(status='active')
        
        # Split by tenant type
        merchant_subs = active_subscriptions.filter(tenant__tenant_type='standard')
        developer_subs = active_subscriptions.filter(tenant__tenant_type='developer')
        
        merchant_mrr = sum(sub.plan.price for sub in merchant_subs if sub.plan)
        developer_mrr = sum(sub.plan.price for sub in developer_subs if sub.plan)
        
        # Subscription growth (last 30 days)
        new_subs_30d = Subscription.objects.filter(
            created_at__gte=days_ago_30
        ).count()
        
        # Churn rate
        total_subs = Subscription.objects.count()
        cancelled_subs = Subscription.objects.filter(status='cancelled').count()
        churn_rate = (cancelled_subs / total_subs * 100) if total_subs > 0 else 0
        
        # ---------------------------------------------------------------------
        # API Usage Analytics
        # ---------------------------------------------------------------------
        total_api_keys = APIKey.objects.count()
        active_api_keys = APIKey.objects.filter(is_active=True).count()
        
        # Webhook events (as proxy for API activity)
        webhook_events_7d = WebhookEvent.objects.filter(
            timestamp__gte=days_ago_7
        ).count()
        
        webhook_success_rate = 0
        if webhook_events_7d > 0:
            successful_webhooks = WebhookEvent.objects.filter(
                timestamp__gte=days_ago_7,
                status_code__lt=400
            ).count()
            webhook_success_rate = (successful_webhooks / webhook_events_7d * 100)
        
        # ---------------------------------------------------------------------
        # Tenant Analytics
        # ---------------------------------------------------------------------
        total_merchants = Tenant.objects.filter(tenant_type='standard').count()
        total_developers = Tenant.objects.filter(tenant_type='developer').count()
        
        active_merchants = Tenant.objects.filter(
            tenant_type='standard',
            subscription__status='active'
        ).distinct().count()
        
        sandbox_tenants = Tenant.objects.filter(is_sandbox=True).count()
        production_tenants = Tenant.objects.filter(is_sandbox=False).count()
        
        plan_revenue = {}
        for p in Plan.objects.all():
            p_rev = sum(s.plan.price for s in p.subscriptions.filter(status='active') if s.plan)
            if p_rev > 0:
                plan_revenue[p.name] = p_rev
        
        # Tenant growth chart (last 30 days)
        tenant_growth = Tenant.objects.filter(
            created_on__gte=days_ago_30
        ).annotate(
            day=TruncDay('created_on')
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # Format for chart
        growth_labels = []
        growth_data = []
        growth_dict = {entry['day']: entry['count'] for entry in tenant_growth}
        
        for i in range(30):
            current_date = (days_ago_30 + timedelta(days=i))
            growth_labels.append(current_date.strftime('%b %d'))
            growth_data.append(growth_dict.get(current_date.replace(hour=0, minute=0, second=0, microsecond=0), 0))
        
        # ---------------------------------------------------------------------
        # Revenue Chart (MRR by month)
        # ---------------------------------------------------------------------
        monthly_revenue = []
        monthly_labels = []
        
        for i in range(6, -1, -1):  # Last 7 months
            month_start = (now - timedelta(days=30*i)).replace(day=1)
            month_subs = Subscription.objects.filter(
                status='active',
                created_at__lte=month_start
            )
            month_mrr = sum(sub.plan.price for sub in month_subs if sub.plan)
            monthly_revenue.append(float(month_mrr))
            monthly_labels.append(month_start.strftime('%b %Y'))
        
        # Update context with platform metrics
        context.update({
            "kpi": [
                {
                    "title": "Merchant MRR",
                    "metric": f"${merchant_mrr:,.2f}",
                    "footer": f"{merchant_subs.count()} active merchants",
                    "icon": "payments",
                },
                {
                    "title": "Developer MRR",
                    "metric": f"${developer_mrr:,.2f}",
                    "footer": f"{developer_subs.count()} active developers",
                    "icon": "code",
                },
                {
                    "title": "Total Merchants",
                    "metric": total_merchants,
                    "footer": f"{active_merchants} active • {sandbox_tenants} sandbox",
                    "icon": "storefront",
                },
                {
                    "title": "Total Developers",
                    "metric": total_developers,
                    "footer": "Platform partners",
                    "icon": "terminal",
                },
            ],
            "progress": [
                {
                    "title": "Subscription Health",
                    "description": f"Churn rate: {churn_rate:.1f}% • {new_subs_30d} new in 30 days",
                    "value": int(100 - churn_rate),
                    "color": "bg-green-500" if churn_rate < 5 else "bg-yellow-500",
                },
                {
                    "title": "Production Tenants",
                    "description": f"{production_tenants} live organizations",
                    "value": production_tenants,
                    "color": "bg-blue-500",
                },
                {
                    "title": "Plan Distribution",
                    "description": " • ".join([f"{k}: ${v:,.0f}" for k, v in list(plan_revenue.items())[:3]]),
                    "value": len(plan_revenue),
                    "color": "bg-purple-500",
                },
            ],
            "chart": {
                "name": "Tenant Growth (Last 30 Days)",
                "type": "line",
                "labels": growth_labels,
                "datasets": [
                    {
                        "label": "New Tenants",
                        "data": growth_data,
                        "backgroundColor": "rgba(79, 70, 229, 0.1)",
                        "borderColor": "#4F46E5",
                        "fill": True,
                    }
                ]
            },
            "chart_secondary": {
                "name": "MRR Trend (Last 7 Months)",
                "type": "bar",
                "labels": monthly_labels,
                "datasets": [
                    {
                        "label": "Monthly Recurring Revenue ($)",
                        "data": monthly_revenue,
                        "backgroundColor": "#10B981",
                    }
                ]
            }
        })
        
        # Serialize chart data for JavaScript
        import json
        context['chart_labels_json'] = json.dumps(growth_labels)
        context['chart_data_json'] = json.dumps(growth_data)
        context['chart_secondary_labels_json'] = json.dumps(monthly_labels)
        context['chart_secondary_data_json'] = json.dumps(monthly_revenue)
        
        print(f"Returning context with keys: {context.keys()}", file=sys.stderr)
        print(f"KPI count: {len(context.get('kpi', []))}", file=sys.stderr)
        print(f"Has chart: {'chart' in context}", file=sys.stderr)
        print(f"Has progress: {'progress' in context}", file=sys.stderr)
        return context

    # =========================================================================
    # TENANT SCHEMA - Tenant-specific Dashboard
    # =========================================================================
    from main.models import Order, Product, Customer, Expense
    
    now = timezone.now()
    days_ago_7 = now - timedelta(days=7)
    
    # Revenue (Completed Orders)
    revenue_data = (
        Order.objects.filter(created_at__gte=days_ago_7, status='completed')
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(total=Sum('total_amount'))
        .order_by('day')
    )
    
    # Expenses
    expense_data = (
        Expense.objects.filter(date__gte=days_ago_7.date())
        .values('date')
        .annotate(total=Sum('amount'))
        .order_by('date')
    )
    
    # Format data for Chart.js
    labels = []
    data_revenue = []
    data_expense = []
    
    rev_dict = {entry['day'].date(): entry['total'] for entry in revenue_data}
    exp_dict = {entry['date']: entry['total'] for entry in expense_data}
    
    for i in range(7):
        current_date = (days_ago_7 + timedelta(days=i)).date()
        labels.append(current_date.strftime('%a'))
        data_revenue.append(float(rev_dict.get(current_date, 0)))
        data_expense.append(float(exp_dict.get(current_date, 0)))

    # KPIs
    total_rev = Order.objects.filter(status='completed').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_exp = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    net_profit = total_rev - total_exp
    
    context.update({
        "kpi": [
            {
                "title": "Total Revenue",
                "metric": f"${total_rev:,.2f}",
                "footer": "Lifetime sales",
                "icon": "payments",
            },
            {
                "title": "Total Expenses",
                "metric": f"${total_exp:,.2f}",
                "footer": "Operational costs",
                "icon": "account_balance_wallet",
            },
            {
                "title": "Net Profit",
                "metric": f"${net_profit:,.2f}",
                "footer": "Revenue - Expenses",
                "icon": "trending_up",
            },
            {
                "title": "Total Orders",
                "metric": Order.objects.count(),
                "footer": "All time",
                "icon": "shopping_cart",
            },
        ],
        "progress": [
            {
                "title": "Low Stock Items",
                "description": f"{Product.objects.filter(stock_quantity__lte=10).count()} products below threshold",
                "value": Product.objects.filter(stock_quantity__lte=10).count(),
                "color": "bg-red-500",
            },
            {
                "title": "Customer Count",
                "description": f"{Customer.objects.count()} registered customers",
                "value": Customer.objects.count(),
                "color": "bg-blue-500",
            },
        ],
        "chart": {
            "name": "Financial Overview (Last 7 Days)",
            "type": "bar",
            "labels": labels,
            "datasets": [
                {
                    "label": "Revenue ($)",
                    "data": data_revenue,
                    "backgroundColor": "#4F46E5",
                },
                {
                    "label": "Expenses ($)",
                    "data": data_expense,
                    "backgroundColor": "#EF4444",
                }
            ]
        }
    })
    
    print(f"[TENANT] Returning context with keys: {context.keys()}", file=sys.stderr)
    print(f"[TENANT] KPI count: {len(context.get('kpi', []))}", file=sys.stderr)
    return context
