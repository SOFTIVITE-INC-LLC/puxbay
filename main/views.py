from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Customer, Category
from .forms import ProductForm, CustomerForm
from accounts.models import UserProfile, Branch
from billing.models import LegalDocument, BlogCategory, BlogTag, BlogPost

@login_required
def dashboard(request):
    try:
        # Public Schema specific handling
        if request.tenant.schema_name == 'public':
            if request.user.is_superuser:
                return redirect('/admin/')
            return redirect('landing')

        profile = getattr(request.user, 'profile', None)
        if not profile:
            # User authenticated but lacks profile for this tenant (or global)
            from django.contrib import messages
            messages.error(request, "Account setup incomplete: No profile found.")
            return redirect('logout')
        
        # Safely get the user's home tenant
        try:
            user_tenant = profile.tenant
        except (AttributeError, Exception): 
            # Tenant might have been deleted but user profile still points to it
            from django.contrib import messages
            messages.error(request, "Your organization configuration is invalid or has been deleted.")
            return redirect('logout')

        # Multi-tenancy check (allow superusers to access any tenant)
        if request.tenant and request.tenant != user_tenant:
            if not request.user.is_superuser:
                # Regular users cannot access other tenants' data
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden(f"Access Denied: You belong to {user_tenant.name}")

        tenant = user_tenant
        
        # Developer Tenant Redirect (Priority)
        if tenant.tenant_type == 'developer':
            return redirect('developer_dashboard')

        # Role-based Redirection
        if profile.role == 'supplier':
            return redirect('supplier_dashboard')
        elif profile.role == 'financial':
            return redirect('profit_loss_report')
        elif profile.role == 'sales':
            if profile.branch:
                return redirect('pos_view', branch_id=profile.branch.id)
            return redirect('landing')
        elif profile.role == 'manager':
            if profile.branch:
                return redirect('branch_dashboard', branch_id=profile.branch.id)
            return redirect('landing')
        elif profile.role != 'admin':
            # Fallback for other non-admin staff
            if profile.branch:
                return redirect('branch_dashboard', branch_id=profile.branch.id)
            return redirect('/')
        
        # Calculate live metrics
        from django.db.models import Sum, Count
        from django.utils import timezone
        from datetime import timedelta
        
        # Total counts (Optimized via TenantMetrics)
        from .models import TenantMetrics
        metrics, created = TenantMetrics.objects.get_or_create(tenant=tenant)
        
        if created:
            # First time setup - populate initial values
            metrics.total_products = Product.objects.filter(tenant=tenant).count()
            metrics.total_orders = Order.objects.filter(tenant=tenant).count()
            metrics.total_customers = Customer.objects.filter(tenant=tenant).count()
            metrics.total_branches = Branch.objects.filter(tenant=tenant).count()
            metrics.save()
            
        products_count = metrics.total_products
        orders_count = metrics.total_orders
        customers_count = metrics.total_customers
        branches_count = metrics.total_branches
        
        # Today's metrics
        today = timezone.now().date()
        today_orders_queryset = Order.objects.filter(tenant=tenant, created_at__date=today).exclude(status='cancelled')
        today_orders_count = today_orders_queryset.count()
        today_sales = today_orders_queryset.filter(status='completed').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # This month's metrics
        month_start = today.replace(day=1)
        month_orders = Order.objects.filter(tenant=tenant, created_at__date__gte=month_start, status='completed')
        month_revenue = month_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Customer Debt
        total_customer_debt = Customer.objects.filter(tenant=tenant).aggregate(total=Sum('outstanding_debt'))['total'] or 0
        
        # Supplier Debt (Accounts Payable)
        from main.models import Supplier
        total_supplier_debt = Supplier.objects.filter(tenant=tenant).aggregate(total=Sum('outstanding_balance'))['total'] or 0
        
        # Recent orders (tenant-wide)
        recent_orders = Order.objects.filter(tenant=tenant).select_related('branch', 'customer').order_by('-created_at')[:10]
        
        # Low stock alerts
        low_stock_products = Product.objects.filter(
            tenant=tenant,
            stock_quantity__lte=10,
            stock_quantity__gt=0
        ).select_related('branch')[:10]
        
        # Get active stock alerts
        from main.models import StockAlert
        active_alerts = StockAlert.objects.filter(
            product__tenant=tenant,
            is_resolved=False
        ).select_related('product', 'product__branch').order_by('-created_at')[:5]
        
        # Chart data: Last 7 days revenue
        import json
        from django.db.models.functions import TruncDate
        
        chart_labels = []
        chart_data = []
        
        seven_days_ago = today - timedelta(days=6)
        sales_by_day = Order.objects.filter(
            tenant=tenant,
            created_at__date__gte=seven_days_ago,
            status='completed'
        ).annotate(
            day=TruncDate('created_at')
        ).values('day').annotate(
            revenue=Sum('total_amount')
        ).order_by('day')
        
        # Mapping to ensure all days are represented
        sales_map = {entry['day']: float(entry['revenue']) for entry in sales_by_day}
        
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            chart_labels.append(date.strftime('%b %d'))
            chart_data.append(sales_map.get(date, 0.0))
        
        # Subscription details
        subscription = getattr(tenant, 'subscription', None)
        
        context = {
            'subscription': subscription,
            'products_count': products_count,
            'orders_count': orders_count,
            'customers_count': customers_count,
            'branches_count': branches_count,
            'today_sales': today_sales,
            'today_orders_count': today_orders_count,
            'month_revenue': month_revenue,
            'total_customer_debt': total_customer_debt,
            'total_supplier_debt': total_supplier_debt,
            'recent_orders': recent_orders,
            'low_stock_products': low_stock_products,
            'active_alerts': active_alerts,
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
        }
    except UserProfile.DoesNotExist:
        context = {}
        
    return render(request, 'main/dashboard.html', context)

from billing.models import PricingPlan, FAQ

def pricing(request):
    if request.tenant.schema_name != 'public':
        return redirect('dashboard')
    
    currency = request.GET.get('currency')
    if currency in ['USD', 'GHS']:
        request.session['currency'] = currency
    
    active_currency = request.session.get('currency', 'GHS')
    
    plans = PricingPlan.objects.all()
    faqs = FAQ.objects.filter(is_visible=True)
    return render(request, 'main/pricing.html', {
        'plans': plans, 
        'faqs': faqs,
        'active_currency': active_currency
    })

def features(request):
    if request.tenant.schema_name != 'public':
        return redirect('dashboard')
    
    from billing.models import FeatureCategory
    
    # Try to get features from database
    db_categories = FeatureCategory.objects.filter(is_active=True).prefetch_related('features')
    
    if db_categories.exists():
        feature_groups = []
        for cat in db_categories:
            group = {
                "name": cat.name,
                "icon": cat.icon,
                "features": [
                    {"title": f.title, "desc": f.desc, "icon": f.icon}
                    for f in cat.features.filter(is_active=True)
                ]
            }
            if group["features"]:
                feature_groups.append(group)
    else:
        # Fallback to hard-coded list if database is empty
        feature_groups = [
            {
                "name": "Omnichannel Sales",
                "icon": "storefront",
                "features": [
                    {"title": "Unified POS", "desc": "Fast, offline-first terminal with barcode support, kitchen routing, and split payments.", "icon": "point_of_sale"},
                    {"title": "E-commerce Storefront", "desc": "Self-hosted online store with real-time inventory sync and secure checkout.", "icon": "shopping_bag"},
                    {"title": "Self-Service Kiosk", "desc": "Interactive kiosk mode for self-checkout and digital menu ordering.", "icon": "settings_remote"},
                    {"title": "Mobile Wallet", "desc": "PWA-based customer wallet for cashless payments and loyalty tracking.", "icon": "account_balance_wallet"},
                    {"title": "Offline Sync", "desc": "Sell without internet; automatic background sync when connection returns.", "icon": "cloud_sync"},
                ]
            },
            {
                "name": "Inventory & Supply Chain",
                "icon": "inventory",
                "features": [
                    {"title": "Global Inventory", "desc": "Real-time stock tracking across unlimited branches and warehouses.", "icon": "inventory_2"},
                    {"title": "Supplier Portal", "desc": "Dedicated vendor access for automated procurement and PO fulfillment.", "icon": "precision_manufacturing"},
                    {"title": "Stock Transfers", "desc": "Secure inventory movements between locations with dual-confirmation audits.", "icon": "swap_horiz"},
                    {"title": "Barcode Engine", "desc": "Bulk generate, customize, and print labels for every product in your catalog.", "icon": "barcode_scanner"},
                    {"title": "Purchase Orders", "desc": "Complete workflow from draft to receiving with automated stock updating.", "icon": "shopping_cart_checkout"},
                ]
            },
            {
                "name": "Business Intelligence",
                "icon": "auto_graph",
                "features": [
                    {"title": "Stock Forecasting", "desc": "AI-driven algorithms predicting stockouts based on local sales velocity.", "icon": "insights"},
                    {"title": "Real-time Analytics", "desc": "Comprehensive dashboards for sales trends, top products, and revenue.", "icon": "analytics"},
                    {"title": "Sales Heatmaps", "desc": "Visualize peak hours and busiest locations with geographical heatmapping.", "icon": "query_stats"},
                    {"title": "Custom Reports", "desc": "Drag-and-drop report builder to export any metric as CSV or PDF.", "icon": "table_chart"},
                    {"title": "Global Command Center", "desc": "Manage pricing and permissions for 100+ branches from one seat.", "icon": "admin_panel_settings"},
                ]
            },
            {
                "name": "Customer Experience",
                "icon": "volunteer_activism",
                "features": [
                    {"title": "Tiered Loyalty", "desc": "Gamify shopping with points, custom tiers, and exclusive member discounts.", "icon": "style"},
                    {"title": "Marketing Hub", "desc": "Broadcast SMS and Email campaigns targeted by customer purchase history.", "icon": "campaign"},
                    {"title": "Feedback Engine", "desc": "Collect and analyze branch-level customer satisfaction scores in real-time.", "icon": "rate_review"},
                    {"title": "Returns & Refunds", "desc": "Managed workflow for item returns, restocking, and automated refunds.", "icon": "assignment_return"},
                    {"title": "CRM Dashboard", "desc": "360° view of customer spending, behavior, and lifecycle management.", "icon": "groups"},
                ]
            },
            {
                "name": "Workforce & ERP",
                "icon": "work_history",
                "features": [
                    {"title": "Biometric Attendance", "desc": "Staff clock-in/out with geofencing and comprehensive attendance reports.", "icon": "schedule"},
                    {"title": "Commission System", "desc": "Rules-based salesperson commissions calculated automatically on every sale.", "icon": "paid"},
                    {"title": "Expense Tracking", "desc": "Log and categorize business overheads with multi-branch allocation.", "icon": "receipt_long"},
                    {"title": "Kitchen Display", "desc": "Kanban-style digital order management for bars and restaurants.", "icon": "view_kanban"},
                    {"title": "2FA Security", "desc": "Enterprise-grade protection with TOTP-based two-factor authentication.", "icon": "verified_user"},
                ]
            },
        ]
    
    return render(request, 'main/features.html', {'feature_groups': feature_groups})


def about(request):
    if request.tenant.schema_name != 'public':
        return redirect('dashboard')
    
    from billing.models import LeadershipMember
    leadership_members = LeadershipMember.objects.filter(is_active=True)
    
    return render(request, 'main/about.html', {
        'leadership_members': leadership_members
    })

from django.core.mail import send_mail
from django.contrib import messages
from .models import ContactMessage

def contact(request):
    if request.tenant.schema_name != 'public':
        return redirect('dashboard')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_content = request.POST.get('message')
        
        if name and email and subject and message_content:
            # Save to database
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_content
            )
            
            # Send Email
            try:
                # Get SEO settings for the contact email if available
                from accounts.models import SEOSettings
                seo_settings = SEOSettings.objects.filter(tenant=request.tenant).first()
                admin_email = seo_settings.contact_email if seo_settings and seo_settings.contact_email else 'admin@puxbay.com'
                
                send_mail(
                    subject=f"Contact Form: {subject}",
                    message=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message_content}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin_email],
                    fail_silently=False,
                )
                messages.success(request, "Your message has been sent successfully! We'll get back to you soon.")
                return redirect('contact')
            except Exception as e:
                # Log error or show message
                messages.error(request, "There was an error sending your message. Please try again later.")
        else:
            messages.warning(request, "Please fill in all fields.")

    return render(request, 'main/contact.html')

def integrations(request):
    if request.tenant.schema_name != 'public':
        return redirect('dashboard')
    return render(request, 'main/integrations.html')

def terms_of_service(request):
    if request.tenant.schema_name != 'public':
        return redirect('dashboard')
    doc = get_object_or_404(LegalDocument, slug='terms-of-service', is_published=True)
    return render(request, 'main/legal/terms.html', {'title': doc.title, 'document': doc})

def privacy_policy(request):
    if request.tenant.schema_name != 'public':
        return redirect('dashboard')
    doc = get_object_or_404(LegalDocument, slug='privacy-policy', is_published=True)
    return render(request, 'main/legal/privacy.html', {'title': doc.title, 'document': doc})

def refund_policy(request):
    if request.tenant.schema_name != 'public':
        return redirect('dashboard')
    doc = get_object_or_404(LegalDocument, slug='refund-policy', is_published=True)
    return render(request, 'main/legal/refund.html', {'title': doc.title, 'document': doc})

def cookie_policy(request):
    if request.tenant.schema_name != 'public':
        return redirect('dashboard')
    doc = get_object_or_404(LegalDocument, slug='cookie-policy', is_published=True)
    return render(request, 'main/legal/cookies.html', {'title': doc.title, 'document': doc})

def blog_home(request):
    if request.tenant.schema_name != 'public':
        return redirect('dashboard')
    
    posts = BlogPost.objects.filter(status='published').order_by('-published_at')
    featured_posts = posts.filter(is_featured=True)[:3]
    categories = BlogCategory.objects.all()
    
    return render(request, 'main/blog/blog_home.html', {
        'posts': posts,
        'featured_posts': featured_posts,
        'categories': categories,
        'title': 'Blog'
    })

def blog_detail(request, slug):
    if request.tenant.schema_name != 'public':
        return redirect('dashboard')
    
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    categories = BlogCategory.objects.all()
    related_posts = BlogPost.objects.filter(category=post.category, status='published').exclude(id=post.id)[:3]
    
    # Next and Previous posts
    prev_post = BlogPost.objects.filter(status='published', published_at__lt=post.published_at).order_by('-published_at').first()
    next_post = BlogPost.objects.filter(status='published', published_at__gt=post.published_at).order_by('published_at').first()
    
    return render(request, 'main/blog/blog_detail.html', {
        'post': post,
        'categories': categories,
        'related_posts': related_posts,
        'prev_post': prev_post,
        'next_post': next_post,
        'title': post.title
    })

def blog_category(request, slug):
    if request.tenant.schema_name != 'public':
        return redirect('dashboard')
    
    category = get_object_or_404(BlogCategory, slug=slug)
    posts = BlogPost.objects.filter(category=category, status='published').order_by('-published_at')
    categories = BlogCategory.objects.all()
    
    return render(request, 'main/blog/blog_home.html', {
        'posts': posts,
        'category': category,
        'categories': categories,
        'title': f'Blog: {category.name}'
    })

def landing(request):
    if request.tenant.schema_name != 'public':
        return redirect('dashboard')
    
    from billing.models import Plan
    plans = Plan.objects.filter(is_active=True).order_by('price')
    active_currency = request.session.get('currency', 'GHS')
    
    return render(request, 'main/landing.html', {
        'plans': plans,
        'active_currency': active_currency
    })

def user_manual(request):
    from documentation.models import DocumentationSection
    
    sections = DocumentationSection.objects.prefetch_related('articles').filter(
        doc_type='manual',
        articles__is_published=True
    ).distinct()
    
    context = {
        'sections': sections,
        'title': 'User Manual'
    }
    return render(request, 'main/user_manual.html', context)

@login_required
def product_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    products = Product.objects.filter(branch=branch).select_related('category', 'supplier', 'branch')
    categories = Category.objects.filter(branch=branch)

    # Search Filter
    search_query = request.GET.get('q', '')
    if search_query:
        from django.db.models import Q
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(sku__icontains=search_query)
        )

    # Category Filter
    selected_category_id = request.GET.get('category', '')
    if selected_category_id:
        products = products.filter(category_id=selected_category_id)

    context = {
        'products': products,
        'branch': branch,
        'categories': categories,
        'search_query': search_query,
        'selected_category_id': int(selected_category_id) if selected_category_id.isdigit() else '',
        'title': 'Products'
    }
    context = {
        'products': products,
        'branch': branch,
        'categories': categories,
        'search_query': search_query,
        'selected_category_id': int(selected_category_id) if selected_category_id.isdigit() else '',
        'title': 'Products'
    }
    return render(request, 'main/product_list.html', context)

@login_required
def product_detail(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    product = get_object_or_404(Product, pk=pk, branch=branch)
    
    context = {
        'branch': branch,
        'product': product,
        'title': product.name
    }
    return render(request, 'main/product_detail.html', context)

@login_required
def product_create(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    if request.user.profile.role == 'sales':
        return redirect('product_list', branch_id=branch.id)
        
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.tenant = request.user.profile.tenant
            product.branch = branch
            product.save()
            return redirect('product_list', branch_id=branch.id)
    else:
        form = ProductForm()
        form.fields['category'].queryset = Category.objects.filter(tenant=request.user.profile.tenant)
        from .models import Supplier
        form.fields['supplier'].queryset = Supplier.objects.filter(tenant=request.user.profile.tenant)
    return render(request, 'main/product_form.html', {'form': form, 'title': 'Add New Product', 'branch': branch})

@login_required
def product_update(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    if request.user.profile.role == 'sales':
        return redirect('product_list', branch_id=branch.id)

    product = get_object_or_404(Product, pk=pk, branch=branch)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list', branch_id=branch.id)
    else:
        form = ProductForm(instance=product)
        form.fields['category'].queryset = Category.objects.filter(tenant=request.user.profile.tenant)
        from .models import Supplier
        form.fields['supplier'].queryset = Supplier.objects.filter(tenant=request.user.profile.tenant)
    return render(request, 'main/product_form.html', {'form': form, 'title': 'Edit Product', 'branch': branch})

@login_required
def product_delete(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    if request.user.profile.role == 'sales':
        return redirect('product_list', branch_id=branch.id)

    product = get_object_or_404(Product, pk=pk, branch=branch)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list', branch_id=branch.id)
    return render(request, 'main/product_confirm_delete.html', {'product': product, 'branch': branch})

# -----------------------------------------------------------------------------
# Customer Management
# -----------------------------------------------------------------------------

@login_required
def customer_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    # Customers are tenant-wide
    customers = Customer.objects.filter(tenant=request.user.profile.tenant).select_related('tier', 'branch').order_by('-created_at')
    
    # Search Filter
    search_query = request.GET.get('q', '')
    if search_query:
        from django.db.models import Q
        customers = customers.filter(
            Q(name__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    context = {
        'branch': branch,
        'customers': customers,
        'search_query': search_query,
        'title': 'Customers'
    }
    return render(request, 'main/customer_list.html', context)

@login_required
def customer_create(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    # Check permissions if strict about Sales role creating customers (usually Sales CAN create customers)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.tenant = request.user.profile.tenant
            customer.save()
            return redirect('customer_list', branch_id=branch.id)
    else:
        form = CustomerForm()
    
    context = {
        'branch': branch,
        'form': form,
        'title': 'Add Customer'
    }
    return render(request, 'main/customer_form.html', context)

@login_required
def customer_update(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    customer = get_object_or_404(Customer, pk=pk, tenant=request.user.profile.tenant)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list', branch_id=branch.id)
    else:
        form = CustomerForm(instance=customer)
        
    context = {
        'branch': branch,
        'form': form,
        'title': 'Edit Customer'
    }
    return render(request, 'main/customer_form.html', context)

@login_required
def customer_delete(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    customer = get_object_or_404(Customer, pk=pk, tenant=request.user.profile.tenant)
    
    # Restrict delete for sales if desired, usually Manager/Admin only
    if request.user.profile.role == 'sales':
        return redirect('customer_list', branch_id=branch.id)

    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list', branch_id=branch.id)
        
    context = {
        'branch': branch,
        'customer': customer,
        'title': 'Delete Customer'
    }
    return render(request, 'main/customer_confirm_delete.html', context)

@login_required
def customer_detail(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    customer = get_object_or_404(Customer, pk=pk, tenant=request.user.profile.tenant)
    orders = customer.orders.filter(branch=branch).select_related('cashier', 'branch').order_by('-created_at') # Show orders for CURRENT branch
    
    context = {
        'branch': branch,
        'customer': customer,
        'orders': orders,
        'title': customer.name
    }
    return render(request, 'main/customer_detail.html', context)

# -----------------------------------------------------------------------------
# Company-Level Reports
# -----------------------------------------------------------------------------

@login_required
def company_financial_report(request):
    """Tenant-wide financial report aggregating all branches"""
    from django.db.models import Sum, Count, F, Avg
    from datetime import datetime, timedelta
    from django.utils import timezone
    from accounts.models import Branch
    
    tenant = request.user.profile.tenant
    
    # Only Admin and Financial users can access company financial reports
    if request.user.profile.role not in ['admin', 'financial']:
        return redirect('dashboard')
    
    # Date Range Filtering
    date_range = request.GET.get('range', 'month')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    now = timezone.now()
    
    if date_range == 'today':
        start_date = now.date()
        end_date = now.date()
    elif date_range == 'week':
        start_date = (now - timedelta(days=7)).date()
        end_date = now.date()
    elif date_range == 'month':
        start_date = (now - timedelta(days=30)).date()
        end_date = now.date()
    elif date_range == 'year':
        start_date = (now - timedelta(days=365)).date()
        end_date = now.date()
    elif date_range == 'custom' and start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:  # 'all' or default
        start_date = None
        end_date = None
    
    # Base queryset for completed orders across TENANT
    orders_query = Order.objects.filter(tenant=tenant, status='completed')
    
    if start_date and end_date:
        orders_query = orders_query.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
    
    # Key Metrics
    total_revenue = orders_query.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = orders_query.count()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Total items sold
    from main.models import OrderItem
    items_query = OrderItem.objects.filter(order__in=orders_query)
    total_items_sold = items_query.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Profit Calculation
    profit_data = items_query.aggregate(
        revenue=Sum(F('price') * F('quantity')),
        cost=Sum(F('product__cost_price') * F('quantity'))
    )
    total_cost = profit_data['cost'] or 0
    total_profit = (profit_data['revenue'] or 0) - total_cost
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Revenue by Branch
    revenue_by_branch = orders_query.values(
        'branch__id', 'branch__name'
    ).annotate(
        revenue=Sum('total_amount'),
        orders=Count('id')
    ).order_by('-revenue')
    
    # Top Products by Revenue
    top_products = items_query.values(
        'product__id', 'product__name', 'product__sku'
    ).annotate(
        revenue=Sum(F('price') * F('quantity')),
        quantity_sold=Sum('quantity')
    ).order_by('-revenue')[:10]
    
    # Revenue by Category
    revenue_by_category = items_query.filter(
        product__category__isnull=False
    ).values(
        'product__category__id', 'product__category__name'
    ).annotate(
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('-revenue')
    
    # Daily Revenue Trend (for chart)
    from django.db.models.functions import TruncDate
    daily_revenue = None
    if start_date and end_date:
        daily_revenue = orders_query.annotate(
            day=TruncDate('created_at')
        ).values('day').annotate(
            revenue=Sum('total_amount')
        ).order_by('day')
    
    # Cashier Performance
    cashier_performance = orders_query.filter(
        cashier__isnull=False
    ).values(
        'cashier__user__username'
    ).annotate(
        order_count=Count('id'),
        total_sales=Sum('total_amount'),
        avg_per_order=Avg('total_amount')
    ).order_by('-total_sales')[:10]
    
    # Product Margins (Company Wide)
    # We need to calculate this manually as it involves cost price which might vary or we want a specific list
    # Reusing the logic from product report for consistency, but top 10
    margin_qs = items_query.values(
        'product__id', 'product__name', 'product__sku'
    ).annotate(
        quantity_sold=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity')),
        cost=Sum(F('product__cost_price') * F('quantity'))
    )
    
    product_margins_company = []
    for item in margin_qs:
        rev = item['revenue'] or 0
        cost = item['cost'] or 0
        profit = rev - cost
        margin_percent = (profit / rev * 100) if rev > 0 else 0
        
        item['profit'] = profit
        item['margin_percent'] = margin_percent
        product_margins_company.append(item)
    
    # Sort by profit desc and take top 10
    product_margins_company.sort(key=lambda x: x['profit'], reverse=True)
    product_margins_company = product_margins_company[:10]

    # Prepare Chart Data
    import json
    
    # daily revenue chart
    chart_dates = []
    chart_revenues = []
    if daily_revenue:
        for entry in daily_revenue:
            chart_dates.append(entry['day'].strftime('%Y-%m-%d'))
            chart_revenues.append(float(entry['revenue']))
            
    # Category chart
    category_labels = []
    category_data = []
    for entry in revenue_by_category:
        category_labels.append(entry['product__category__name'])
        category_data.append(float(entry['revenue']))

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'total_items_sold': total_items_sold,
        'total_profit': total_profit,
        'profit_margin': profit_margin,
        'revenue_by_branch': revenue_by_branch,
        'top_products': top_products,
        'revenue_by_category': revenue_by_category,
        'daily_revenue': daily_revenue,
        'cashier_performance': cashier_performance,
        'product_margins_company': product_margins_company, # Added this
        'chart_dates': json.dumps(chart_dates), # Added
        'chart_revenues': json.dumps(chart_revenues), # Added
        'category_labels': json.dumps(category_labels), # Added
        'category_data': json.dumps(category_data), # Added
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        'title': 'Company Financial Report'
    }
    return render(request, 'main/company_financial_report.html', context)

@login_required
def company_product_report(request):
    """Tenant-wide product analysis report"""
    from django.db.models import Sum, Count, F, Case, When, Value, DecimalField
    from main.models import OrderItem
    from datetime import datetime, timedelta
    from django.utils import timezone

    tenant = request.user.profile.tenant
    
    # Only Admin and Financial users can access
    if request.user.profile.role not in ['admin', 'financial']:
        return redirect('dashboard')
    
    # Date Range Filtering
    date_range = request.GET.get('range', 'all')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    now = timezone.now()
    
    if date_range == 'today':
        filter_start = now.date()
        filter_end = now.date()
    elif date_range == 'week':
        filter_start = (now - timedelta(days=7)).date()
        filter_end = now.date()
    elif date_range == 'month':
        filter_start = (now - timedelta(days=30)).date()
        filter_end = now.date()
    elif date_range == 'year':
        filter_start = (now - timedelta(days=365)).date()
        filter_end = now.date()
    elif date_range == 'custom' and start_date and end_date:
        try:
            filter_start = datetime.strptime(start_date, '%Y-%m-%d').date()
            filter_end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            filter_start = None
            filter_end = None
    else:  # 'all' or default
        filter_start = None
        filter_end = None

    # Base Products
    products = Product.objects.filter(tenant=tenant, is_active=True)
    
    # Inventory value
    inventory_value = products.aggregate(
        total_value=Sum(F('stock_quantity') * F('price'))
    )['total_value'] or 0
    
    # Low stock
    low_stock_items = products.filter(
        stock_quantity__lte=F('low_stock_threshold'),
        stock_quantity__gt=0
    )
    
    # Out of stock items
    out_of_stock_items = products.filter(stock_quantity=0)
    out_of_stock_count = out_of_stock_items.count()
    
    # Sales Data Aggregation
    items_query = OrderItem.objects.filter(order__tenant=tenant, order__status='completed')
    
    if filter_start and filter_end:
        items_query = items_query.filter(order__created_at__date__gte=filter_start, order__created_at__date__lte=filter_end)
    
    # Best Sellers
    best_sellers = items_query.values(
        'product__id', 'product__name'
    ).annotate(
        quantity_sold=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('-quantity_sold')[:10]

    # Revenue by Category
    revenue_by_category = items_query.filter(
        product__category__isnull=False
    ).values(
        'product__category__id', 'product__category__name'
    ).annotate(
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('-revenue')
    
    # Product Margins
    # We grab the raw data and calculate margin % in python to avoid complex DB math
    margin_qs = items_query.values(
        'product__id', 'product__name', 'product__sku'
    ).annotate(
        quantity_sold=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity')),
        cost=Sum(F('product__cost_price') * F('quantity'))
    )
    
    product_margins = []
    for item in margin_qs:
        rev = item['revenue'] or 0
        cost = item['cost'] or 0
        profit = rev - cost
        margin_percent = (profit / rev * 100) if rev > 0 else 0
        
        item['profit'] = profit
        item['margin_percent'] = margin_percent
        product_margins.append(item)
    
    # Sort by profit desc
    product_margins.sort(key=lambda x: x['profit'], reverse=True)
    
    context = {
        'total_products': products.count(),
        'inventory_value': inventory_value,
        'low_stock_count': low_stock_items.count(),
        'out_of_stock_count': out_of_stock_count,
        'low_stock_items': low_stock_items[:20], 
        'out_of_stock_items': out_of_stock_items[:20],
        'title': 'Company Product Report',
        'best_sellers': best_sellers,
        'revenue_by_category': revenue_by_category,
        'product_margins': product_margins,
        'date_range': date_range,
        'start_date': filter_start,
        'end_date': filter_end,
        'first_branch': tenant.branches.first(),
    }
    
    return render(request, 'main/company_product_report.html', context)

def test_404(request):
    """Test view to preview the custom 404 page during development"""
    return render(request, '404.html', status=404)


def offline_view(request):
    """
    Render offline fallback page
    """
    return render(request, 'offline.html')

def set_currency(request):
    """Set the active currency for the session."""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            currency_code = data.get('currency')
            if currency_code:
                request.session['currency'] = currency_code
                request.session.modified = True
                return JsonResponse({'status': 'ok', 'currency': currency_code})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@login_required
def submit_feedback(request):
    """
    Handle feedback reports (bugs, features, recommendations) from tenants.
    Saves to database and sends email notification to Puxbay.
    """
    from .forms import FeedbackForm
    from django.http import JsonResponse
    from django.core.mail import send_mail
    from django.urls import reverse
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.tenant = request.tenant
            feedback.user = request.user
            feedback.save()
            
            # Prepare email content
            subject = f"[{feedback.get_report_type_display().upper()}] {feedback.subject} - {request.tenant.name}"
            admin_url = request.build_absolute_uri(reverse('admin:main_feedbackreport_change', args=[feedback.id]))
            
            context = {
                'feedback': feedback,
                'admin_url': admin_url,
            }
            
            html_message = render_to_string('emails/feedback_submitted.html', context)
            plain_message = strip_tags(html_message)
            
            try:
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    ['feedback@puxbay.com'],
                    html_message=html_message,
                    fail_silently=True,
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Feedback email failed: {str(e)}")

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success', 
                    'message': 'Thank you! Your report has been submitted successfully.'
                })
            
            from django.contrib import messages
            messages.success(request, "Thank you! Your report has been submitted successfully.")
            return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
            
    return redirect('dashboard')

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        "Disallow: /api/",
        "Disallow: /checkout/",
        f"Sitemap: http://{settings.ROOT_DOMAIN}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
