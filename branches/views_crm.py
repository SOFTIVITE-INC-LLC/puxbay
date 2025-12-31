from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import models
from accounts.models import Branch
from main.models import Product, Order, OrderItem, Category, Customer
from main.forms import CategoryForm, ProductForm, CustomerForm
from .forms import BranchSettingsForm
import json
from django.utils import timezone

@login_required
def dashboard(request, branch_id):
    from django.db.models import Sum, Count
    from accounts.models import UserProfile
    
    # Enforce Branch Access Control
    try:
        profile = request.user.profile
        # Admin can access all. Staff/Manager can only access their assigned branch.
        if profile.role != 'admin' and (not profile.branch or profile.branch.id != branch_id):
             # For a smoother UX, if they are staff but trying to access wrong branch, redirect to THEIR branch
             if profile.branch:
                 return redirect('branch_dashboard', branch_id=profile.branch.id)
             else:
                 return redirect('/') # Should not happen if data integrity is kept, but safe fallback
    except:
        return redirect('/')

    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    # Calculate real branch statistics
    # Total Sales (completed orders)
    sales_data = Order.objects.filter(
        branch=branch, 
        status='completed'
    ).aggregate(
        total_revenue=Sum('total_amount'),
        order_count=Count('id')
    )
    
    # Product statistics
    products = Product.objects.filter(branch=branch, is_active=True)
    total_products = products.count()
    low_stock_products = products.filter(
        stock_quantity__lte=models.F('low_stock_threshold')
    ).count()
    
    # Staff count for this branch
    staff_count = UserProfile.objects.filter(branch=branch).count()
    
    context = {
        'branch': branch,
        'total_revenue': sales_data['total_revenue'] or 0,
        'sales_count': sales_data['order_count'] or 0,
        'staff_count': staff_count,
        'stock_count': total_products,
        'low_stock_count': low_stock_products,
    }

    # Add Sales-Specific Stats
    if request.user.profile.role == 'sales':
        my_orders = Order.objects.filter(branch=branch, cashier=request.user.profile)
        
        # Total Sales
        total_sales = my_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        context['my_total_sales'] = total_sales
        
        # Total Orders
        context['my_total_orders'] = my_orders.count()
        
        # Recent Transactions
        context['my_recent_orders'] = my_orders.order_by('-created_at')[:5]

    # -------------------------------------------------------------------------
    # ANALYTICS DATA PREPARATION (CACHED)
    # -------------------------------------------------------------------------
    from django.core.cache import cache
    
    cache_key = f'branch_dashboard_analytics_{branch.id}_{timezone.now().date()}'
    analytics_data = cache.get(cache_key)
    
    if not analytics_data:
        from django.db.models import F
        from django.db.models.functions import TruncDate, ExtractHour
        import datetime

        # 1. Sales Trend (Last 30 Days)
        thirty_days_ago = timezone.now() - datetime.timedelta(days=30)
        sales_trend = Order.objects.filter(
            branch=branch,
            status='completed',
            created_at__gte=thirty_days_ago
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            amount=Sum('total_amount')
        ).order_by('date')

        # Fill in missing dates
        sales_trend_dict = {item['date']: item['amount'] for item in sales_trend}
        sales_trend_data = []
        labels_trend = []
        
        current_date = thirty_days_ago.date()
        end_date = timezone.now().date()
        
        while current_date <= end_date:
            labels_trend.append(current_date.strftime('%b %d'))
            sales_trend_data.append(float(sales_trend_dict.get(current_date, 0)))
            current_date += datetime.timedelta(days=1)

        # 2. Top Selling Products (By Revenue)
        top_products = OrderItem.objects.filter(
            order__branch=branch,
            order__status='completed',
            order__created_at__gte=thirty_days_ago
        ).values('product__name').annotate(
            revenue=Sum(F('price') * F('quantity'))
        ).order_by('-revenue')[:5]
        
        top_products_labels = [item['product__name'] for item in top_products]
        top_products_data = [float(item['revenue']) for item in top_products]

        # 3. Peak Hours (All Time or Last 30 Days - let's do Last 30 Days for relevance)
        peak_hours = Order.objects.filter(
            branch=branch,
            status='completed',
            created_at__gte=thirty_days_ago
        ).annotate(
            hour=ExtractHour('created_at')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')

        peak_hours_dict = {item['hour']: item['count'] for item in peak_hours}
        peak_hours_labels = [f"{h:02d}:00" for h in range(24)]
        peak_hours_data = [peak_hours_dict.get(h, 0) for h in range(24)]
        
        analytics_data = {
            'sales_trend_labels': json.dumps(labels_trend),
            'sales_trend_data': json.dumps(sales_trend_data),
            'top_products_labels': json.dumps(top_products_labels),
            'top_products_data': json.dumps(top_products_data),
            'peak_hours_labels': json.dumps(peak_hours_labels),
            'peak_hours_data': json.dumps(peak_hours_data),
        }
        
        # Cache for 5 minutes (300 seconds)
        cache.set(cache_key, analytics_data, 300)

    context.update(analytics_data)

    return render(request, 'branches/dashboard.html', context)

# -----------------------------------------------------------------------------
# Category Management
# -----------------------------------------------------------------------------

@login_required
def category_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    categories = Category.objects.filter(branch=branch)
    
    context = {
        'branch': branch,
        'categories': categories,
        'title': 'Categories'
    }
    return render(request, 'main/category_list.html', context)

@login_required
def category_detail(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    category = get_object_or_404(Category, pk=pk, branch=branch)
    products = category.products.filter(is_active=True)
    
    context = {
        'branch': branch,
        'category': category,
        'products': products,
        'title': category.name
    }
    return render(request, 'main/category_detail.html', context)

@login_required
def category_create(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.tenant = request.user.profile.tenant
            category.branch = branch
            category.save()
            return redirect('category_list', branch_id=branch.id)
    else:
        form = CategoryForm()
    
    context = {
        'branch': branch,
        'form': form,
        'title': 'Add Category'
    }
    return render(request, 'main/category_form.html', context)

@login_required
def category_update(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    category = get_object_or_404(Category, pk=pk, branch=branch)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list', branch_id=branch.id)
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'branch': branch,
        'form': form,
        'title': 'Edit Category'
    }
    return render(request, 'main/category_form.html', context)

@login_required
def category_delete(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    category = get_object_or_404(Category, pk=pk, branch=branch)
    
    if request.method == 'POST':
        category.delete()
        return redirect('category_list', branch_id=branch.id)
    
    context = {
        'branch': branch,
        'category': category,
        'title': 'Delete Category'
    }
    return render(request, 'main/category_confirm_delete.html', context)

# -----------------------------------------------------------------------------
# Product Management
# -----------------------------------------------------------------------------

@login_required
def product_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    products = Product.objects.filter(branch=branch, is_active=True).select_related('category')
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    filter_type = request.GET.get('filter')
    
    if category_id:
        products = products.filter(category_id=category_id)
        
    if filter_type == 'low_stock':
        from django.db.models import F
        products = products.filter(stock_quantity__lte=F('low_stock_threshold'))
        
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        from django.db.models import Q
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(sku__icontains=search_query) |
            Q(barcode__icontains=search_query)
        )
        
    context = {
        'branch': branch,
        'products': products,
        'categories': Category.objects.filter(branch=branch),
        'title': 'Products',
        'search_query': search_query,
        'selected_category': int(category_id) if category_id else None
    }
    return render(request, 'main/product_list.html', context)

@login_required
def product_create(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
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
        # Filter categories for this branch
        form.fields['category'].queryset = Category.objects.filter(branch=branch)
    
    context = {
        'branch': branch,
        'form': form,
        'title': 'Add Product'
    }
    return render(request, 'main/product_form.html', context)

@login_required
def product_update(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    product = get_object_or_404(Product, pk=pk, branch=branch)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list', branch_id=branch.id)
    else:
        form = ProductForm(instance=product)
        # Filter categories for this branch
        form.fields['category'].queryset = Category.objects.filter(branch=branch)
    
    context = {
        'branch': branch,
        'form': form,
        'title': 'Edit Product'
    }
    return render(request, 'main/product_form.html', context)

@login_required
def product_delete(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    product = get_object_or_404(Product, pk=pk, branch=branch)
    
    if request.method == 'POST':
        product.delete()
        return redirect('product_list', branch_id=branch.id)
    
    context = {
        'branch': branch,
        'product': product,
        'title': 'Delete Product'
    }
    return render(request, 'main/product_confirm_delete.html', context)

# -----------------------------------------------------------------------------
# Customer Management
# -----------------------------------------------------------------------------

@login_required
def customer_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    customers = Customer.objects.filter(tenant=request.user.profile.tenant)
    
    # Search
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
        'title': 'Customers',
        'search_query': search_query
    }
    return render(request, 'main/customer_list.html', context)

@login_required
def customer_detail(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    customer = get_object_or_404(Customer, pk=pk, tenant=request.user.profile.tenant)
    orders = Order.objects.filter(customer=customer, branch=branch).order_by('-created_at')
    
    context = {
        'branch': branch,
        'customer': customer,
        'orders': orders,
        'title': customer.name
    }
    return render(request, 'main/customer_detail.html', context)

@login_required
def customer_create(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
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
def pos_view(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    # OPTIMIZED: Added select_related for category and prefetch_related for batches to avoid N+1 queries
    products = Product.objects.filter(branch=branch, is_active=True, stock_quantity__gt=0)\
        .select_related('category')\
        .prefetch_related('batches')
    
    categories = Category.objects.filter(branch=branch)
    customers = Customer.objects.filter(tenant=request.user.profile.tenant)
    
    # Serialize products
    products_json = []
    for p in products:
        products_json.append({
            'id': str(p.id),
            'name': p.name,
            'price': float(p.price),
            'stock': p.stock_quantity,
            'sku': p.sku,
            'category': p.category.name if p.category else 'Uncategorized',
            'category_id': str(p.category.id) if p.category else 0,
            'is_batch_tracked': p.is_batch_tracked,
            'batches': [
                {
                    'id': str(b.id),
                    'batch_number': b.batch_number,
                    'expiry': b.expiry_date.strftime('%Y-%m-%d') if b.expiry_date else None,
                    'quantity': b.quantity
                } 
                for b in p.batches.filter(branch=branch, quantity__gt=0).order_by('expiry_date')
            ] if p.is_batch_tracked else []
        })
        
    # Serialize customers
    customers_json = []
    for c in customers:
        customers_json.append({
            'id': str(c.id),
            'name': c.name,
            'phone': c.phone or '',
            'email': c.email or ''
        })

    # Serialize categories
    categories_json = []
    for c in categories:
        categories_json.append({
            'id': str(c.id),
            'name': c.name
        })

    context = {
        'branch': branch,
        'products_json': json.dumps(products_json),
        'customers_json': json.dumps(customers_json),
        'categories_json': json.dumps(categories_json),
        'categories': categories,
    }
    return render(request, 'branches/pos.html', context)

@login_required
def pos_checkout(request, branch_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
        
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        customer_id = data.get('customer_id')
        
        if not items:
            return JsonResponse({'success': False, 'error': 'Cart is empty'})

        # Calculate total and validate stock
        total_amount = 0
        order_items = []
        
        # Transaction atomic would be ideal here in real app
        for item in items:
            product = Product.objects.get(pk=item['id'], branch=branch)
            qty = int(item['quantity'])
            
            # Validate Batch for Tracked Items
            batch = None
            if product.is_batch_tracked:
                batch_id = item.get('batch_id')
                if not batch_id:
                     return JsonResponse({'success': False, 'error': f'Batch selection required for {product.name}'})
                
                from .models import StockBatch
                batch = StockBatch.objects.get(pk=batch_id, product=product, branch=branch)
                if batch.quantity < qty:
                     return JsonResponse({'success': False, 'error': f'Insufficient stock in batch {batch.batch_number}'})
                
                # prepare to deduct from batch later
                item['batch_obj'] = batch

            if product.stock_quantity < qty:
                return JsonResponse({'success': False, 'error': f'Not enough stock for {product.name}'})
            
            total_amount += (product.price * qty)
            order_items.append({'product': product, 'qty': qty, 'price': product.price, 'batch': batch})
            
        # Resolve Customer
        customer = None
        if customer_id:
            customer = Customer.objects.filter(pk=customer_id, tenant=request.user.profile.tenant).first()

        # Create Order
        order = Order.objects.create(
            tenant=request.user.profile.tenant,
            branch=branch,
            cashier=request.user.profile,
            customer=customer,
            total_amount=total_amount,
            status='completed'
        )
        
        # Create Order Items and Update Stock
        from .models import StockMovement
        for item in order_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['qty'],
                price=item['price']
            )
            
            # Deduct Global Stock
            item['product'].stock_quantity -= item['qty']
            item['product'].save()
            
            # Deduct Batch Stock if applicable
            batch = item.get('batch')
            if batch:
                batch.quantity -= item['qty']
                batch.save()
            
            # Create Audit Log
            StockMovement.objects.create(
                tenant=branch.tenant,
                branch=branch,
                product=item['product'],
                batch=batch,
                quantity_change=-item['qty'],
                balance_after=item['product'].stock_quantity,
                movement_type='sale',
                reference=f"Order #{order.id}",
                created_by=request.user.profile,
                notes=f"POS Sale"
            )
            
        return JsonResponse({'success': True, 'order_id': str(order.id)})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# -----------------------------------------------------------------------------
# Reporting Views
# -----------------------------------------------------------------------------

@login_required
def transaction_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    orders = Order.objects.filter(branch=branch).select_related('cashier', 'cashier__user').order_by('-created_at')
    
    # Filtering
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    date_start = request.GET.get('date_start', '')
    date_end = request.GET.get('date_end', '')

    if search_query:
        if search_query.isdigit():
            orders = orders.filter(id=search_query)
        # Could extend to search by cashier username if desired, generally order ID is key

    if status_filter:
        orders = orders.filter(status=status_filter)

    if date_start:
        orders = orders.filter(created_at__date__gte=date_start)
    
    if date_end:
        orders = orders.filter(created_at__date__lte=date_end)

    context = {
        'branch': branch,
        'orders': orders,
        'title': 'Transactions',
        'search_query': search_query,
        'status_filter': status_filter,
        'date_start': date_start,
        'date_end': date_end,
    }
    return render(request, 'branches/transaction_list.html', context)

@login_required
def sales_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    # Order items for orders belonging to this branch
    sales = OrderItem.objects.filter(order__branch=branch).select_related('order', 'product').order_by('-order__created_at')
    
    # Filtering
    search_query = request.GET.get('q', '')
    date_start = request.GET.get('date_start', '')
    date_end = request.GET.get('date_end', '')

    if search_query:
        from django.db.models import Q
        sales = sales.filter(
            Q(product__name__icontains=search_query) | 
            Q(product__sku__icontains=search_query) |
            Q(order__id__icontains=search_query)
        )
    
    if date_start:
        sales = sales.filter(order__created_at__date__gte=date_start)
    
    if date_end:
        sales = sales.filter(order__created_at__date__lte=date_end)

    context = {
        'branch': branch,
        'sales': sales,
        'title': 'Sales Items',
        'search_query': search_query,
        'date_start': date_start,
        'date_end': date_end,
    }
    return render(request, 'branches/sales_list.html', context)

@login_required
def transaction_detail(request, branch_id, order_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    order = get_object_or_404(Order, pk=order_id, branch=branch)
    items = order.items.select_related('product').all()
    
    context = {
        'branch': branch,
        'order': order,
        'items': items,
        'title': f'Transaction #{order.id}'
    }
    return render(request, 'branches/transaction_detail.html', context)

@login_required
def transaction_receipt(request, branch_id, order_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    order = get_object_or_404(Order, pk=order_id, branch=branch)
    items = order.items.select_related('product').all()
    
    context = {
        'branch': branch,
        'order': order,
        'items': items,
    }
    return render(request, 'branches/receipt.html', context)

@login_required
def settings_view(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    # Only Admin or Manager can access settings
    if request.user.profile.role not in ['admin', 'manager']:
        return redirect('dashboard', branch_id=branch.id)
        
    if request.method == 'POST':
        form = BranchSettingsForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            return redirect('settings_view', branch_id=branch.id)
    else:
        form = BranchSettingsForm(instance=branch)
        
    context = {
        'branch': branch,
        'form': form,
    }
    return render(request, 'branches/settings.html', context)

# -----------------------------------------------------------------------------
# Financial Reports
# -----------------------------------------------------------------------------

@login_required
def branch_financial_report(request, branch_id):
    from django.db.models import Sum, Count, F, Q, Avg
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    # Only Admin or Manager can access financial reports
    if request.user.profile.role not in ['admin', 'manager']:
        return redirect('branch_dashboard', branch_id=branch.id)
    
    # Date Range Filtering
    date_range = request.GET.get('range', 'month')  # today, week, month, year, all, custom
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
    
    # Base queryset for completed orders
    orders_query = Order.objects.filter(branch=branch, status='completed')
    
    if start_date and end_date:
        orders_query = orders_query.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
    
    # Key Metrics
    total_revenue = orders_query.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = orders_query.count()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Total items sold
    items_query = OrderItem.objects.filter(order__in=orders_query)
    total_items_sold = items_query.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Profit Calculation (Revenue - Cost)
    profit_data = items_query.aggregate(
        revenue=Sum(F('price') * F('quantity')),
        cost=Sum(F('product__cost_price') * F('quantity'))
    )
    total_cost = profit_data['cost'] or 0
    total_profit = (profit_data['revenue'] or 0) - total_cost
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
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
    
    # Cashier Performance
    cashier_performance = orders_query.values(
        'cashier__id', 'cashier__user__username'
    ).annotate(
        total_sales=Sum('total_amount'),
        order_count=Count('id'),
        avg_per_order=Avg('total_amount')
    ).order_by('-total_sales')
    
    # Daily Revenue Trend (last 30 days or within date range)
    if date_range in ['today', 'week', 'month', 'custom']:
        trend_start = start_date if start_date else (now - timedelta(days=30)).date()
        trend_end = end_date if end_date else now.date()
        
        daily_revenue = orders_query.filter(
            created_at__date__gte=trend_start,
            created_at__date__lte=trend_end
        ).extra(
            select={'day': 'DATE(created_at)'}
        ).values('day').annotate(
            revenue=Sum('total_amount'),
            orders=Count('id')
        ).order_by('day')
    else:
        daily_revenue = []
    
    # Product Analysis
    products = Product.objects.filter(branch=branch, is_active=True)
    
    # Inventory value
    inventory_value = products.aggregate(
        total_value=Sum(F('stock_quantity') * F('price'))
    )['total_value'] or 0
    
    # Low stock and out of stock
    low_stock_items = products.filter(
        stock_quantity__lte=F('low_stock_threshold'),
        stock_quantity__gt=0
    ).values('id', 'name', 'sku', 'stock_quantity', 'low_stock_threshold', 'price')[:10]
    
    out_of_stock_count = products.filter(stock_quantity=0).count()
    
    # Product profit margins (from sales data)
    from django.db.models import Case, When, Value, DecimalField
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
    ).order_by('-profit')[:10]
    
    # Worst performers (products with low sales in the period)
    worst_performers = items_query.values(
        'product__id', 'product__name', 'product__sku'
    ).annotate(
        quantity_sold=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('quantity_sold')[:5]
    
    context = {
        'branch': branch,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        
        # Key Metrics
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'total_items_sold': total_items_sold,
        'total_profit': total_profit,
        'profit_margin': profit_margin,
        
        # Detailed Data
        'top_products': top_products,
        'revenue_by_category': revenue_by_category,
        'cashier_performance': cashier_performance,
        'daily_revenue': list(daily_revenue),
        
        # Product Analysis
        'inventory_value': inventory_value,
        'low_stock_items': low_stock_items,
        'low_stock_count': low_stock_items.count() if hasattr(low_stock_items, 'count') else len(list(low_stock_items)),
        'out_of_stock_count': out_of_stock_count,
        'product_margins': product_margins,
        'worst_performers': worst_performers,
    }
    
    return render(request, 'branches/branch_financial_report.html', context)

@login_required
def branch_product_report(request, branch_id):
    """Branch-level product analysis report"""
    from django.db.models import Sum, Count, F, Case, When, Value, DecimalField
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    # Only Admin or Manager can access product reports
    if request.user.profile.role not in ['admin', 'manager']:
        return redirect('branch_dashboard', branch_id=branch.id)
    
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
    elif date_range == 'all':
        start_date = None
        end_date = None
    elif date_range == 'custom' and start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        start_date = (now - timedelta(days=30)).date()
        end_date = now.date()
    
    # Base queryset for orders
    orders_query = Order.objects.filter(branch=branch, status='completed')
    if start_date and end_date:
        orders_query = orders_query.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
    
    items_query = OrderItem.objects.filter(order__in=orders_query)
    
    # Product Analysis
    products = Product.objects.filter(branch=branch, is_active=True)
    
    # Inventory value
    inventory_value = products.aggregate(
        total_value=Sum(F('stock_quantity') * F('price'))
    )['total_value'] or 0
    
    # Low stock and out of stock
    low_stock_items = products.filter(
        stock_quantity__lte=F('low_stock_threshold'),
        stock_quantity__gt=0
    ).values('id', 'name', 'sku', 'stock_quantity', 'low_stock_threshold', 'price')[:20]
    
    out_of_stock_items = products.filter(stock_quantity=0).values('id', 'name', 'sku', 'price')[:20]
    out_of_stock_count = products.filter(stock_quantity=0).count()
    
    # Product profit margins (from sales data)
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
    ).order_by('-profit')[:20]
    
    # Best sellers
    best_sellers = items_query.values(
        'product__id', 'product__name', 'product__sku'
    ).annotate(
        quantity_sold=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('-quantity_sold')[:10]  # Limit to top 10
    
    # Worst performers
    worst_performers = items_query.values(
        'product__id', 'product__name', 'product__sku'
    ).annotate(
        quantity_sold=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('quantity_sold')[:10]
    
    # Revenue by category
    revenue_by_category = items_query.filter(
        product__category__isnull=False
    ).values(
        'product__category__id', 'product__category__name'
    ).annotate(
        revenue=Sum(F('price') * F('quantity')),
        quantity_sold=Sum('quantity')
    ).order_by('-revenue')
    
    context = {
        'branch': branch,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        
        # Inventory Metrics
        'inventory_value': inventory_value,
        'low_stock_items': low_stock_items,
        'low_stock_count': low_stock_items.count() if hasattr(low_stock_items, 'count') else len(list(low_stock_items)),
        'out_of_stock_items': out_of_stock_items,
        'out_of_stock_count': out_of_stock_count,
        
        # Product Performance
        'product_margins': product_margins,
        'best_sellers': best_sellers,
        'worst_performers': worst_performers,
        'revenue_by_category': revenue_by_category,
    }
    
    return render(request, 'branches/branch_product_report.html', context)

@login_required
def company_financial_report(request):
    from django.db.models import Sum, Count, F
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    # Only admin can access company-wide reports
    if request.user.profile.role != 'admin':
        return redirect('home')
    
    tenant = request.user.profile.tenant
    
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
    else:
        start_date = None
        end_date = None
    
    # Base queryset for all completed orders in company
    orders_query = Order.objects.filter(tenant=tenant, status='completed')
    
    if start_date and end_date:
        orders_query = orders_query.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
    
    # Company-wide Metrics
    total_revenue = orders_query.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = orders_query.count()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Revenue by Branch
    revenue_by_branch = orders_query.filter(
        branch__isnull=False
    ).values(
        'branch__id', 'branch__name'
    ).annotate(
        revenue=Sum('total_amount'),
        order_count=Count('id')
    ).order_by('-revenue')
    
    # Top Products Company-Wide
    items_query = OrderItem.objects.filter(order__in=orders_query)
    top_products = items_query.values(
        'product__id', 'product__name', 'product__sku'
    ).annotate(
        revenue=Sum(F('price') * F('quantity')),
        quantity_sold=Sum('quantity')
    ).order_by('-revenue')[:10]
    
    # Total Profit
    profit_data = items_query.aggregate(
        revenue=Sum(F('price') * F('quantity')),
        cost=Sum(F('product__cost_price') * F('quantity'))
    )
    total_cost = profit_data['cost'] or 0
    total_profit = (profit_data['revenue'] or 0) - total_cost
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Product Analysis - Company Wide
    all_products = Product.objects.filter(tenant=tenant, is_active=True)
    
    # Company-wide inventory value
    company_inventory_value = all_products.aggregate(
        total_value=Sum(F('stock_quantity') * F('price'))
    )['total_value'] or 0
    
    # Low stock alerts across all branches
    company_low_stock_count = all_products.filter(
        stock_quantity__lte=F('low_stock_threshold'),
        stock_quantity__gt=0
    ).count()
    
    # Out of stock count
    company_out_of_stock = all_products.filter(stock_quantity=0).count()
    
    # Product profit margins company-wide
    from django.db.models import Case, When, Value, DecimalField
    product_margins_company = items_query.values(
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
    ).order_by('-profit')[:10]
    
    context = {
        'tenant': tenant,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        
        # Key Metrics
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'total_profit': total_profit,
        'profit_margin': profit_margin,
        
        # Detailed Data
        'revenue_by_branch': revenue_by_branch,
        'top_products': top_products,
        
        # Product Analysis
        'company_inventory_value': company_inventory_value,
        'company_low_stock_count': company_low_stock_count,
        'company_out_of_stock': company_out_of_stock,
        'product_margins_company': product_margins_company,
    }
    
    return render(request, 'branches/company_financial_report.html', context)


# ============================================================================
# OFFLINE SYNC API ENDPOINTS
# ============================================================================

@login_required
def sync_transaction(request):
    """
    API endpoint to receive and process queued offline transactions
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        uuid = data.get('uuid')
        transaction_type = data.get('type')
        transaction_data = data.get('data')
        
        if not all([uuid, transaction_type, transaction_data]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Check if already synced (prevent duplicates)
        if Order.objects.filter(offline_uuid=uuid).exists():
            return JsonResponse({
                'status': 'already_synced',
                'message': 'Transaction already processed'
            })
        
        # Process transaction based on type
        if transaction_type == 'transaction':
            # Create order from offline data
            branch_id = transaction_data.get('branch_id')
            branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
            
            # Get or create customer
            customer_id = transaction_data.get('customer_id')
            customer = None
            if customer_id:
                customer = Customer.objects.filter(id=customer_id, branch=branch).first()
            
            # Create order
            order = Order.objects.create(
                branch=branch,
                customer=customer,
                cashier=request.user.profile,
                total_amount=transaction_data.get('total_amount', 0),
                payment_method=transaction_data.get('payment_method', 'cash'),
                status='completed',
                offline_uuid=uuid  # Store UUID to prevent duplicates
            )
            
            # Create order items
            items = transaction_data.get('items', [])
            for item_data in items:
                product = Product.objects.get(id=item_data['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                
                # Update inventory
                product.stock_quantity -= item_data['quantity']
                product.save()
            
            return JsonResponse({
                'status': 'success',
                'order_id': order.id,
                'message': 'Transaction synced successfully'
            })
        
        else:
            return JsonResponse({'error': 'Unknown transaction type'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_sync_data(request, branch_id):
    """
    API endpoint to fetch data for offline caching
    Returns last 500 transactions, all products, customers, and categories
    """
    try:
        # Verify branch access
        branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
        profile = request.user.profile
        
        if profile.role != 'admin' and (not profile.branch or profile.branch.id != branch_id):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Get last 500 transactions
        transactions = Order.objects.filter(
            branch=branch,
            status='completed'
        ).order_by('-created_at')[:500].values(
            'id', 'customer_id', 'total_amount', 'payment_method',
            'status', 'created_at', 'cashier__user__username'
        )
        
        # Get all active products for this branch
        products = Product.objects.filter(
            branch=branch,
            is_active=True
        ).values(
            'id', 'name', 'sku', 'price', 'cost_price', 'stock_quantity',
            'low_stock_threshold', 'category_id', 'branch_id'
        )
        
        # Get all customers for this branch
        customers = Customer.objects.filter(
            branch=branch
        ).values(
            'id', 'name', 'email', 'phone', 'branch_id'
        )
        
        # Get all categories for this branch
        categories = Category.objects.filter(
            branch=branch
        ).values(
            'id', 'name', 'branch_id'
        )
        
        # Convert QuerySets to lists and handle datetime serialization
        from django.core.serializers.json import DjangoJSONEncoder
        
        return JsonResponse({
            'transactions': list(transactions),
            'products': list(products),
            'customers': list(customers),
            'categories': list(categories),
            'cached_at': timezone.now().isoformat()
        }, encoder=DjangoJSONEncoder)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_inventory(request, branch_id):
    """
    API endpoint to get current inventory levels for stock synchronization
    """
    try:
        # Verify branch access
        branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
        profile = request.user.profile
        
        if profile.role != 'admin' and (not profile.branch or profile.branch.id != branch_id):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Get all active products with current stock levels
        products = Product.objects.filter(
            branch=branch,
            is_active=True
        ).values('id', 'stock_quantity')
        
        return JsonResponse(list(products), safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def offline_page(request):
    """
    Offline fallback page
    """
    return render(request, 'offline.html')

# -----------------------------------------------------------------------------
# Stock Transfer Views
# -----------------------------------------------------------------------------

from .models import StockTransfer, StockTransferItem
from .forms_transfer import StockTransferForm

@login_required
def transfer_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    # Sent Transfers
    sent_transfers = StockTransfer.objects.filter(source_branch=branch).order_by('-created_at')
    
    # Received Transfers
    received_transfers = StockTransfer.objects.filter(destination_branch=branch).order_by('-created_at')
    
    context = {
        'branch': branch,
        'sent_transfers': sent_transfers,
        'received_transfers': received_transfers,
        'title': 'Stock Transfers'
    }
    return render(request, 'branches/transfer_list.html', context)

@login_required
def transfer_create(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    products = Product.objects.filter(branch=branch, is_active=True, stock_quantity__gt=0)
    
    if request.method == 'POST':
        form = StockTransferForm(request.POST, user=request.user, branch_id=branch.id)
        if form.is_valid():
            try:
                # Extract Items
                items_data = request.POST.get('items_json')
                if not items_data:
                    raise Exception("No items selected")
                
                items = json.loads(items_data)
                
                # atomic transaction
                from django.db import transaction
                with transaction.atomic():
                    transfer = form.save(commit=False)
                    transfer.tenant = request.user.profile.tenant
                    transfer.source_branch = branch
                    transfer.created_by = request.user.profile
                    
                    # Generate Reference
                    import uuid
                    transfer.reference_id = f"TRF-{uuid.uuid4().hex[:8].upper()}"
                    transfer.save()
                    
                    for item in items:
                        product = Product.objects.get(id=int(item['product_id']), branch=branch)
                        qty = int(item['quantity'])
                        
                        if product.stock_quantity < qty:
                             raise Exception(f"Insufficient stock for {product.name}")
                        
                        # Create Item
                        StockTransferItem.objects.create(
                            transfer=transfer,
                            product=product,
                            quantity=qty
                        )
                        
                        # Deduct from Source immediately (as per design choice: "Pending" = reserved/in-transit)
                        product.stock_quantity -= qty
                        product.save()
            
                return redirect('transfer_detail', branch_id=branch.id, pk=transfer.id)
                
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = StockTransferForm(user=request.user, branch_id=branch.id)
        
    context = {
        'branch': branch,
        'form': form,
        'products': products,
        'title': 'New Stock Transfer'
    }
    return render(request, 'branches/transfer_form.html', context)

@login_required
def transfer_detail(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    transfer = get_object_or_404(StockTransfer, pk=pk, tenant=request.user.profile.tenant)
    
    # Permissions: User must be in source or destination branch (or admin)
    user_branch_id = request.user.profile.branch.id if request.user.profile.branch else None
    if request.user.profile.role != 'admin':
         if user_branch_id not in [transfer.source_branch.id, transfer.destination_branch.id]:
             return redirect('transfer_list', branch_id=branch.id)

    context = {
        'branch': branch,
        'transfer': transfer,
        'is_destination': (branch.id == transfer.destination_branch.id),
        'title': f'Transfer {transfer.reference_id}'
    }
    return render(request, 'branches/transfer_detail.html', context)

@login_required
def transfer_receive(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    transfer = get_object_or_404(StockTransfer, pk=pk, destination_branch=branch)
    
    if request.method == 'POST' and transfer.status == 'pending':
        from django.db import transaction
        with transaction.atomic():
            transfer.status = 'completed'
            transfer.completed_at = timezone.now()
            transfer.save()
            
            # Add stock to destination
            for item in transfer.items.all():
                # Find product in local branch by SKU or Name
                # Priority: SKU
                dest_product = Product.objects.filter(
                    branch=branch, 
                    sku=item.product.sku
                ).first()
                
                if not dest_product:
                    # Try Name
                    dest_product = Product.objects.filter(
                         branch=branch,
                         name=item.product.name
                    ).first()
                
                if dest_product:
                    dest_product.stock_quantity += item.quantity
                    dest_product.save()
                else:
                    # Create new product in destination
                    p = item.product
                    Product.objects.create(
                        tenant=branch.tenant,
                        branch=branch,
                        category=None, # Or try to match category by name? Keep simple for now.
                        name=p.name,
                        sku=p.sku,
                        price=p.price,
                        stock_quantity=item.quantity,
                        description=p.description,
                        expiry_date=p.expiry_date,
                        barcode=p.barcode,
                        cost_price=p.cost_price,
                        low_stock_threshold=p.low_stock_threshold
                    )
        return redirect('transfer_detail', branch_id=branch.id, pk=transfer.id)
        
    return redirect('transfer_list', branch_id=branch.id)


# -----------------------------------------------------------------------------
# Purchase Order Views
# -----------------------------------------------------------------------------

from .models import Supplier, PurchaseOrder, PurchaseOrderItem
from .forms_po import SupplierForm, PurchaseOrderForm

@login_required
def supplier_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    suppliers = Supplier.objects.filter(tenant=request.user.profile.tenant).order_by('name')
    
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.tenant = request.user.profile.tenant
            supplier.save()
            return redirect('supplier_list', branch_id=branch.id)
    else:
        form = SupplierForm()
        
    context = {
        'branch': branch,
        'suppliers': suppliers,
        'form': form,
        'title': 'Suppliers'
    }
    return render(request, 'branches/supplier_list.html', context)

@login_required
def purchase_order_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    orders = PurchaseOrder.objects.filter(branch=branch).order_by('-created_at')
    
    context = {
        'branch': branch,
        'orders': orders,
        'title': 'Purchase Orders'
    }
    return render(request, 'branches/po_list.html', context)

@login_required
def purchase_order_create(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    products = Product.objects.filter(branch=branch, is_active=True)
    
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, tenant=request.user.profile.tenant)
        if form.is_valid():
            try:
                items_data = request.POST.get('items_json')
                if not items_data:
                     raise Exception("No items selected")
                items = json.loads(items_data)
                
                from django.db import transaction
                with transaction.atomic():
                    po = form.save(commit=False)
                    po.tenant = request.user.profile.tenant
                    po.branch = branch
                    po.created_by = request.user.profile
                    po.status = 'ordered'
                    
                    import uuid
                    po.reference_id = f"PO-{uuid.uuid4().hex[:8].upper()}"
                    po.save()
                    
                    total_cost = 0
                    for item in items:
                        product = Product.objects.get(id=int(item['product_id']), branch=branch)
                        qty = int(item['quantity'])
                        data_cost = item.get('cost')
                        cost = float(data_cost) if data_cost else float(product.cost_price)
                        
                        PurchaseOrderItem.objects.create(
                            po=po,
                            product=product,
                            quantity=qty,
                            unit_cost=cost
                        )
                        total_cost += (cost * qty)
                    
                    po.total_cost = total_cost
                    po.save()
                    
                return redirect('purchase_order_detail', branch_id=branch.id, pk=po.id)
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = PurchaseOrderForm(tenant=request.user.profile.tenant)
        
    context = {
        'branch': branch,
        'form': form,
        'products': products,
        'title': 'New Purchase Order'
    }
    return render(request, 'branches/po_form.html', context)

@login_required
def purchase_order_detail(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    po = get_object_or_404(PurchaseOrder, pk=pk, branch=branch)
    
    context = {
        'branch': branch,
        'po': po,
        'title': f'{po.reference_id}'
    }
    return render(request, 'branches/po_detail.html', context)

@login_required
def purchase_order_receive(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    po = get_object_or_404(PurchaseOrder, pk=pk, branch=branch)
    
    if request.method == 'POST' and po.status == 'ordered':
        from django.db import transaction
        with transaction.atomic():
            po.status = 'received'
            po.save()
            
            # Update Stock
            for item in po.items.all():
                product = item.product
                product.stock_quantity += item.quantity
                product.cost_price = item.unit_cost
                product.save()
                
        return redirect('purchase_order_detail', branch_id=branch.id, pk=po.id)
    return redirect('purchase_order_list', branch_id=branch.id)


@login_required
def low_stock_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    # Filter products where stock <= threshold (default 10 if None)
    from django.db.models import F
    
    # We can assume threshold is set, or default to some value. 
    # Logic: stock_quantity <= low_stock_threshold
    low_stock_products = Product.objects.filter(
        branch=branch, 
        is_active=True,
        stock_quantity__lte=F('low_stock_threshold')
    )
    
    context = {
        'branch': branch,
        'products': low_stock_products,
        'title': 'Low Stock Alerts'
    }
    return render(request, 'branches/low_stock_list.html', context)
