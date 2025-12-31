from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.db import models
from django.db.models import Q
from branches.services.reporting import ReportingService
from django.db.models import Sum, Count, F
from accounts.models import Branch, Attendance, UserProfile
from main.models import Product, Order, OrderItem, Category, Customer, GiftCard, LoyaltyTransaction, StoreCreditTransaction, CRMSettings
from main.forms import CategoryForm, ProductForm, CustomerForm, GiftCardForm
from django.contrib import messages
# from .forms import BranchSettingsForm removed here, imported below
from main.models import (
    Product, Order, OrderItem, Category, Customer, GiftCard, 
    LoyaltyTransaction, StoreCreditTransaction, CRMSettings,
    Expense, ExpenseCategory, TaxConfiguration
)
from main.forms import CategoryForm, ProductForm, CustomerForm, GiftCardForm
from main.forms_financial import ExpenseForm
from .forms import BranchSettingsForm, ProductImportForm
from .services.payments import PaymentService
from .services.purchase_orders import PurchaseOrderService
from main.forms_credit import CustomerPaymentForm
from main.models import CustomerCreditTransaction
from .services.transfers import TransferService
import json
import csv
import requests
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.utils import timezone
import datetime
from api.auth import require_api_key_django

from accounts.utils import merchant_only

@login_required
@merchant_only
def dashboard(request, branch_id):
    from django.db.models import Sum, Count
    from accounts.models import UserProfile
    
    # Enforce Branch Access Control
    try:
        profile = request.user.profile
        # Admin and Financial can access all. Staff/Manager can only access their assigned branch.
        if profile.role not in ['admin', 'financial'] and (not profile.branch or profile.branch.id != branch_id):
             # For a smoother UX, if they are staff but trying to access wrong branch, redirect to THEIR branch
             if profile.branch:
                 return redirect('branch_dashboard', branch_id=profile.branch.id)
             else:
                 return redirect('/') # Should not happen if data integrity is kept, but safe fallback
    except:
        return redirect('/')

    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    # Branch-specific Customer Debt (customers who have purchased from this branch)
    from main.models import Customer, Supplier
    from branches.models import PurchaseOrder
    
    # Get unique customers who have orders at this branch
    branch_customer_ids = Order.objects.filter(
        branch=branch,
        customer__isnull=False
    ).values_list('customer_id', flat=True).distinct()
    
    total_customer_debt = Customer.objects.filter(
        id__in=branch_customer_ids
    ).aggregate(total=Sum('outstanding_debt'))['total'] or 0
    
    # Branch-specific Supplier Debt (suppliers who supply to this branch)
    # Get unique suppliers who have supplied products to this branch
    branch_supplier_ids = PurchaseOrder.objects.filter(
        branch=branch
    ).values_list('supplier_id', flat=True).distinct()
    
    total_supplier_debt = Supplier.objects.filter(
        id__in=branch_supplier_ids
    ).aggregate(total=Sum('outstanding_balance'))['total'] or 0
    
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
    
    # Products missing barcodes
    missing_barcodes_count = products.filter(
        models.Q(barcode__isnull=True) | models.Q(barcode='')
    ).count()
    
    # Staff count for this branch
    staff_count = UserProfile.objects.filter(branch=branch).count()
    
    # Smart Stock Recommendations
    from .models import InventoryRecommendation
    recommendations = InventoryRecommendation.objects.filter(
        branch=branch, 
        is_dismissed=False
    ).select_related('product')[:5]

    # Online Stats (Online Store + Kiosk)
    online_orders = Order.objects.filter(branch=branch, status='completed', ordering_type__in=['online', 'kiosk'])
    online_stats = online_orders.aggregate(
        revenue=Sum('total_amount'),
        count=Count('id')
    )
    
    # --- CHART DATA ---
    from django.utils import timezone
    from django.db.models.functions import TruncDate, ExtractHour
    import json
    
    # 1. Sales Trend (Last 7 days)
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)
    daily_sales = Order.objects.filter(
        branch=branch,
        status='completed',
        created_at__gte=seven_days_ago
    ).annotate(
        day=TruncDate('created_at')
    ).values('day').annotate(
        total=Sum('total_amount')
    ).order_by('day')
    
    sales_trend_labels = [entry['day'].strftime('%b %d') for entry in daily_sales]
    sales_trend_data = [float(entry['total']) for entry in daily_sales]
    
    # 2. Top 5 Products by Revenue
    from main.models import OrderItem
    from django.db.models import F
    top_products = OrderItem.objects.filter(
        order__branch=branch,
        order__status='completed'
    ).values('product__name').annotate(
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('-revenue')[:5]
    
    top_products_labels = [p['product__name'] for p in top_products]
    top_products_data = [float(p['revenue']) for p in top_products]
    
    # 3. Peak Hours (Aggregated by Hour)
    peak_hours = Order.objects.filter(
        branch=branch,
        status='completed'
    ).annotate(
        hour=ExtractHour('created_at')
    ).values('hour').annotate(
        count=Count('id')
    ).order_by('hour')
    
    # Fill all 24 hours
    hours_map = {h['hour']: h['count'] for h in peak_hours}
    peak_hours_labels = [f"{h}:00" for h in range(24)]
    peak_hours_data = [hours_map.get(h, 0) for h in range(24)]

    context = {
        'branch': branch,
        'total_revenue': sales_data['total_revenue'] or 0,
        'sales_count': sales_data['order_count'] or 0,
        'staff_count': staff_count,
        'stock_count': total_products,
        'low_stock_count': low_stock_products,
        'recommendations': recommendations,
        'online_revenue': online_stats['revenue'] or 0,
        'online_orders_count': online_stats['count'] or 0,
        'missing_barcodes_count': missing_barcodes_count,
        # Chart Data
        'sales_trend_labels': json.dumps(sales_trend_labels),
        'sales_trend_data': json.dumps(sales_trend_data),
        'top_products_labels': json.dumps(top_products_labels),
        'top_products_data': json.dumps(top_products_data),
        'peak_hours_labels': json.dumps(peak_hours_labels),
        'peak_hours_data': json.dumps(peak_hours_data),
        'manager': UserProfile.objects.filter(branch=branch, role='manager').first(),
        'total_customer_debt': total_customer_debt,
        'total_supplier_debt': total_supplier_debt,
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
        context['my_recent_orders'] = my_orders.select_related('customer', 'cashier').order_by('-created_at')[:5]

    return render(request, 'branches/dashboard.html', context)

# -----------------------------------------------------------------------------
# Category Management
# -----------------------------------------------------------------------------

from django.views.decorators.cache import cache_page

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
    products = category.products.filter(is_active=True).select_related('category')
    
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
    if category_id:
        products = products.filter(category_id=category_id)

    # Filter by Stock Status
    filter_type = request.GET.get('filter')
    if filter_type == 'low_stock':
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
        'selected_category': category_id  # Keep as UUID string, don't convert to int
    }
    return render(request, 'main/product_list.html', context)

@login_required
def product_detail(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    product = get_object_or_404(Product, pk=pk, branch=branch)
    
    # Imports for related data
    from .models import StockMovement, PurchaseOrderItem
    from main.models import ProductHistory
    
    # Stock History
    movements = StockMovement.objects.filter(product=product, branch=branch).order_by('-created_at')
    
    # Product History (Audit Trail)
    history = ProductHistory.objects.filter(product=product).select_related('changed_by', 'changed_by__user').order_by('-changed_at')
    
    # Purchase Orders
    po_items = PurchaseOrderItem.objects.filter(product=product, po__branch=branch).select_related('po', 'po__supplier').order_by('-po__created_at')
    
    context = {
        'branch': branch,
        'product': product,
        'movements': movements,
        'history': history,
        'po_items': po_items,
        'title': product.name
    }
    return render(request, 'branches/product_detail.html', context)

@login_required
def product_create(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    from main.forms import ProductForm, ProductComponentFormSet
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = ProductComponentFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            product = form.save(commit=False)
            product.tenant = request.user.profile.tenant
            product.branch = branch
            product.save()
            
            formset.instance = product
            formset.save()
            
            return redirect('product_list', branch_id=branch.id)
    else:
        form = ProductForm()
        formset = ProductComponentFormSet()
    
    # Filter formset product choices to current branch
    # Note: Ideally we filter component_product queryset here
    # formset.forms[0].fields['component_product'].queryset... but for new empty forms it's tricky without a custom formset or form init
    # For now, we rely on standard behavior, might show all products. Optimize later.
    
    context = {
        'branch': branch,
        'form': form,
        'formset': formset,
        'title': 'Add Product'
    }
    return render(request, 'main/product_form.html', context)

@login_required
def export_products(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    from .xlsx_utils import XLSXGenerator
    
    generator = XLSXGenerator()
    
    # Header - 16 Fields
    headers = [
        'Name', 'SKU', 'Category', 'Price', 'Wholesale Price', 
        'Min Wholesale Qty', 'Cost Price', 'Stock Quantity', 'Low Stock Threshold', 
        'Barcode', 'Expiry Date (YYYY-MM-DD)', 'Batch Number', 'Invoice Number', 
        'Description', 'Is Active', 'Image URL',
        'Manufacturing Date (YYYY-MM-DD)', 'Country of Origin', 'Manufacturer Name', 'Manufacturer Address'
    ]
    generator.writerow(headers)
    
    # Template download
    if request.GET.get('template'):
        generator.writerow([
            'Sample Product', 'SKU12345', 'General', '10.00', '8.00', 
            '5', '5.00', '100', '10', 
            '123456789', '2025-12-31', 'BATCH001', 'INV-2023-001', 
            'Product description here', 'TRUE', 'https://example.com/sample-image.jpg',
            '2023-01-01', 'USA', 'Acme Corp', '123 Factory Rd'
        ])
    else:
        products = Product.objects.filter(branch=branch, is_active=True).select_related('category')
        for p in products:
            generator.writerow([
                p.name,
                p.sku,
                p.category.name if p.category else '',
                p.price,
                p.wholesale_price,
                p.minimum_wholesale_quantity,
                p.cost_price,
                p.stock_quantity,
                p.low_stock_threshold,
                p.barcode or '',
                p.expiry_date.strftime('%Y-%m-%d') if p.expiry_date else '',
                p.batch_number or '',
                p.invoice_waybill_number or '',
                p.description or '',
                'TRUE' if p.is_active else 'FALSE',
                request.build_absolute_uri(p.image.url) if p.image else '',
                p.manufacturing_date.strftime('%Y-%m-%d') if p.manufacturing_date else '',
                p.country_of_origin or '',
                p.manufacturer_name or '',
                p.manufacturer_address or ''
            ])

    response = HttpResponse(
        generator.generate(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="products_{branch.name}_{timezone.now().strftime("%Y%m%d")}.xlsx"'
    return response

@login_required
def import_products(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    from .forms import ProductImportForm
    import base64
    
    if request.method == 'POST':
        form = ProductImportForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['import_file']
            try:
                # Validate file type
                if not f.name.endswith('.xlsx'):
                    messages.error(request, 'Please upload a valid .xlsx file.')
                    return redirect('import_products', branch_id=branch.id)
                
                # Read file content
                file_content = f.read()
                
                # Try to use Celery for async processing
                try:
                    # FORCE SYNC for debugging (User reported async issues)
                    raise Exception("Forced Synchronous Import")

                    from .tasks import import_products_task
                    
                    # Encode as base64 for safe Celery serialization
                    file_content_b64 = base64.b64encode(file_content).decode('utf-8')
                    
                    # Queue the task asynchronously
                    task = import_products_task.delay(
                        str(request.user.profile.tenant.id),
                        str(branch.id),
                        file_content_b64
                    )
                    
                    messages.success(
                        request, 
                        f"Product import started in the background. "
                        f"This may take a few moments for large files. "
                        f"Refresh the product list to see imported items."
                    )
                except Exception as celery_err:
                    # Fallback to synchronous processing if Celery is not available
                    messages.warning(request, "Background processing unavailable, importing synchronously...")
                    
                    from .xlsx_utils import XLSXParser
                    from .services.inventory import InventoryService
                    
                    parser = XLSXParser(file_content)
                    service = InventoryService(tenant=request.user.profile.tenant, branch=branch)
                    
                    results = service.import_from_parser(parser)
                    success_count = results['success']
                    skip_count = results['skipped']
                    errors = results['errors']
                    
                    if success_count > 0:
                        messages.success(request, f"Successfully imported {success_count} products.")
                    
                    if skip_count > 0:
                        messages.info(request, f"Skipped {skip_count} empty or incomplete rows.")
                    
                    if errors:
                        for err in errors[:5]:
                            messages.warning(request, err)
                        if len(errors) > 5:
                            messages.warning(request, f"...and {len(errors) - 5} more errors.")
                
                return redirect('product_list', branch_id=branch.id)
                
            except Exception as e:
                messages.error(request, f"Import failed: {str(e)}")
    else:
        form = ProductImportForm()

    context = {
        'branch': branch,
        'form': form,
        'title': 'Import Products'
    }
    return render(request, 'branches/product_import.html', context)


@login_required
def product_update(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    product = get_object_or_404(Product, pk=pk, branch=branch)
    from main.forms import ProductForm, ProductComponentFormSet
    
    if request.method == 'POST':
        old_instance = Product.objects.get(pk=pk)
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ProductComponentFormSet(request.POST, instance=product)
        
        if form.is_valid() and formset.is_valid():
            from accounts.services.audit_service import AuditService
            changes = AuditService.get_field_diff(old_instance, product)
            form.save()
            formset.save()
            
            if changes:
                AuditService.log_action(
                    request, 
                    'update', 
                    f"Updated product: {product.name}",
                    target_model='Product',
                    target_object_id=product.id,
                    changes=changes
                )
            return redirect('product_list', branch_id=branch.id)
    else:
        form = ProductForm(instance=product)
        # Filter categories for this branch
        form.fields['category'].queryset = Category.objects.filter(branch=branch)
        formset = ProductComponentFormSet(instance=product)
    
    context = {
        'branch': branch,
        'form': form,
        'formset': formset,
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
    customers = Customer.objects.filter(tenant=request.user.profile.tenant).select_related('tier')
    
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
    
    # Loyalty History
    loyalty_history = LoyaltyTransaction.objects.filter(customer=customer).order_by('-created_at')[:50]
    
    # Store Credit History
    credit_history = StoreCreditTransaction.objects.filter(customer=customer).order_by('-created_at')[:50]
    
    # Debt/Credit History
    debt_history = CustomerCreditTransaction.objects.filter(customer=customer).order_by('-created_at')[:50]
    
    payment_form = CustomerPaymentForm()
    
    context = {
        'branch': branch,
        'customer': customer,
        'orders': orders,
        'loyalty_history': loyalty_history,
        'credit_history': credit_history,
        'debt_history': debt_history,
        'payment_form': payment_form,
        'title': customer.name
    }
    return render(request, 'main/customer_detail.html', context)

@login_required
def record_customer_payment(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    customer = get_object_or_404(Customer, pk=pk, tenant=request.user.profile.tenant)
    
    if request.method == 'POST':
        form = CustomerPaymentForm(request.POST)
        if form.is_valid():
            try:
                PaymentService.record_customer_payment(
                    customer=customer,
                    amount=form.cleaned_data['amount'],
                    user=request.user,
                    notes=form.cleaned_data['notes']
                )
                messages.success(request, f"Payment of {branch.currency_symbol}{form.cleaned_data['amount']} recorded for {customer.name}.")
            except Exception as e:
                messages.error(request, f"Error recording payment: {str(e)}")
        else:
            messages.error(request, "Invalid payment details. Please check the amount.")
            
    return redirect('customer_detail', branch_id=branch.id, pk=customer.id)

@login_required
def customer_create(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.tenant = request.user.profile.tenant
            customer.branch = branch  # Set the branch
            customer.save()
            messages.success(request, f'Customer "{customer.name}" created successfully.')
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
        old_instance = Customer.objects.get(pk=pk)
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            from accounts.services.audit_service import AuditService
            changes = AuditService.get_field_diff(old_instance, customer)
            form.save()
            
            if changes:
                AuditService.log_action(
                    request, 
                    'update', 
                    f"Updated customer: {customer.name}",
                    target_model='Customer',
                    target_object_id=customer.id,
                    changes=changes
                )
            messages.success(request, f'Customer "{customer.name}" updated successfully.')
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
@merchant_only
def pos_view(request, branch_id):
    from .services.pos import POSService
    
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    tenant = request.user.profile.tenant
    pos_api_key = tenant.pos_api_key
    
    if not pos_api_key:
        import secrets
        import hashlib
        from accounts.models import APIKey
        
        # Generate a stable internal key
        raw_key = "pb_" + secrets.token_urlsafe(32)
        prefix = raw_key[:8]
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        # Save to APIKey model for validation
        APIKey.objects.create(
            tenant=tenant,
            branch=branch,
            name="Internal POS Key",
            key_prefix=prefix,
            key_hash=key_hash
        )
        
        # Save raw key to tenant (encrypted)
        tenant.pos_api_key = raw_key
        tenant.save()
        pos_api_key = raw_key

    # Optimized for Instant Shell Loading (Phase 6)
    from storefront.models import StorefrontSettings
    store_settings = StorefrontSettings.objects.filter(tenant=tenant).first()
    payment_config = {
        'stripe_enabled': False,
        'stripe_key': store_settings.stripe_public_key if store_settings and store_settings.enable_stripe else None,
        'paystack_enabled': False,
        'paystack_key': store_settings.paystack_public_key if store_settings and store_settings.enable_paystack else None,
        'currency_code': branch.currency_code,
        'logo_url': branch.logo.url if branch.logo else None
    }
    
    if store_settings:
        payment_config['stripe_enabled'] = bool(store_settings.enable_stripe and store_settings.stripe_public_key)
        payment_config['paystack_enabled'] = bool(store_settings.enable_paystack and store_settings.paystack_public_key)

    context = {
        'branch': branch,
        'products_json': '[]', # Hydrated via API
        'customers_json': '[]', # Hydrated via API
        'categories_json': '[]', # Hydrated via API
        'payment_config': json.dumps(payment_config),
        'pos_api_key': pos_api_key,
    }
    return render(request, 'branches/pos.html', context)

@login_required
@merchant_only
def pos_data_api(request, branch_id):
    """
    JSON API for fetching latest POS data.
    """
    from .services.pos import POSService
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    pos_service = POSService(request.user.profile.tenant, request.user.profile)
    
    data = pos_service.get_pos_data(branch)
    return JsonResponse({
        "status": "success",
        "code": 200,
        "data": data,
        "message": "POS data hydrated successfully"
    })


from django.views.decorators.csrf import csrf_exempt

@require_api_key_django
def pos_checkout(request, branch_id):
    try:
        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': 'Invalid request method'})
        
        # Validation for Profile
        profile = getattr(request.user, 'profile', None)
        if not profile:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[POS Checkout] Error: User {request.user} has no profile attached")
            return JsonResponse({'success': False, 'error': 'User profile not found. Please refresh the page.'}, status=401)
            
        branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)
            
        service = PaymentService(request.user, branch, data)
        result = service.process_checkout()
        
        if result['success']:
            return JsonResponse({'success': True, 'order_id': str(result['order_id'])})
        else:
            return JsonResponse({'success': False, 'error': result['error']})
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f"Unexpected error in pos_checkout: {str(e)}")
        return JsonResponse({'success': False, 'error': f"Server Error: {str(e)}"}, status=500)

# -----------------------------------------------------------------------------
# Reporting Views
# -----------------------------------------------------------------------------

@login_required
def transaction_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    orders = Order.objects.filter(branch=branch).select_related('cashier', 'cashier__user').order_by('-created_at')
    
    # Restrict visibility for salespersons
    if request.user.profile.role == 'sales':
        orders = orders.filter(cashier=request.user.profile)
    
    # Filtering
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    date_start = request.GET.get('date_start', '')
    date_end = request.GET.get('date_end', '')

    if search_query:
        try:
            import uuid
            # Check if valid UUID
            uuid_obj = uuid.UUID(search_query)
            orders = orders.filter(id=uuid_obj)
        except ValueError:
            # Otherwise search by order_number (exact match due to possible encryption)
            # fallback to exact case-insensitive if not encrypted, but exact is safest for encrypted
            orders = orders.filter(order_number=search_query)

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
    
    # Restrict visibility for salespersons
    if request.user.profile.role == 'sales':
        sales = sales.filter(order__cashier=request.user.profile)
    
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
def online_transaction_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    orders = Order.objects.filter(branch=branch, ordering_type__in=['online', 'kiosk']).select_related('cashier', 'cashier__user').order_by('-created_at')
    
    # Restrict visibility for salespersons
    # Salespersons can see their own orders OR any pending online/kiosk orders
    if request.user.profile.role == 'sales':
        from django.db.models import Q
        orders = orders.filter(Q(cashier=request.user.profile) | Q(status='pending'))
    
    # Filtering
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    date_start = request.GET.get('date_start', '')
    date_end = request.GET.get('date_end', '')

    if search_query:
        try:
            import uuid
            uuid_obj = uuid.UUID(search_query)
            orders = orders.filter(id=uuid_obj)
        except ValueError:
            orders = orders.filter(order_number=search_query)

    if status_filter:
        orders = orders.filter(status=status_filter)

    if date_start:
        orders = orders.filter(created_at__date__gte=date_start)
    
    if date_end:
        orders = orders.filter(created_at__date__lte=date_end)

    context = {
        'branch': branch,
        'orders': orders,
        'title': 'Online Transactions',
        'search_query': search_query,
        'status_filter': status_filter,
        'date_start': date_start,
        'date_end': date_end,
        'is_online': True,
    }
    return render(request, 'branches/transaction_list.html', context)

@login_required
def online_sales_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    # Order items for ONLINE orders belonging to this branch
    sales = OrderItem.objects.filter(order__branch=branch, order__ordering_type__in=['online', 'kiosk']).select_related('order', 'product').order_by('-order__created_at')
    
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
        'title': 'Online Sales Items',
        'search_query': search_query,
        'date_start': date_start,
        'date_end': date_end,
        'is_online': True,
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
        'title': f'Transaction #{order.order_number or order.id}'
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
    
    # Only Admin, Manager, or Financial can access settings
    if request.user.profile.role not in ['admin', 'manager', 'financial']:
        return redirect('branch_dashboard', branch_id=branch.id)
        
    if request.method == 'POST':
        form = BranchSettingsForm(request.POST, request.FILES, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, 'Branch settings updated successfully!')
            return redirect('settings_view', branch_id=branch.id)
        else:
            messages.error(request, 'Failed to update settings. Please check the form for errors.')
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
    
    # Only Admin, Manager, or Financial can access financial reports
    if request.user.profile.role not in ['admin', 'manager', 'financial']:
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
    
    # Date Range Filtering
    date_range = request.GET.get('range', 'month')
    start_str = request.GET.get('start_date', '')
    end_str = request.GET.get('end_date', '')
    
    from branches.services.reporting import ReportingService
    reporting_service = ReportingService(tenant=request.user.profile.tenant, branch=branch)
    
    start_date, end_date = reporting_service.get_date_range(date_range, start_str, end_str)
    
    # Get Analytics via Service
    financial_summary = reporting_service.get_financial_summary(start_date, end_date)
    product_insights = reporting_service.get_product_insights(start_date, end_date, limit=10)
    top_products = reporting_service.get_top_products(start_date, end_date, limit=10)
    revenue_by_category = reporting_service.get_revenue_by_category(start_date, end_date)
    cashier_performance = reporting_service.get_cashier_performance(start_date, end_date)
    daily_revenue = reporting_service.get_daily_revenue(start_date, end_date)
    
    context = {
        'branch': branch,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        
        # Financial Metrics
        **financial_summary,
        
        # Detailed Analytics
        'top_products': top_products,
        'revenue_by_category': revenue_by_category,
        'cashier_performance': cashier_performance,
        'daily_revenue': list(daily_revenue),
        
        # Product Analysis (Unpacked)
        **product_insights,
        'low_stock_count': len(product_insights.get('low_stock_items', []))
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
    start_str = request.GET.get('start_date', '')
    end_str = request.GET.get('end_date', '')
    
    reporting_service = ReportingService(tenant=request.user.profile.tenant, branch=branch)
    
    start_date, end_date = reporting_service.get_date_range(date_range, start_str, end_str)
    
    # Get Analytics via Service
    product_insights = reporting_service.get_product_insights(start_date, end_date, limit=20)
    revenue_by_category = reporting_service.get_revenue_by_category(start_date, end_date)
    
    context = {
        'branch': branch,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        'revenue_by_category': revenue_by_category,
        **product_insights  # Unpack insights (top_products, best_sellers, worst_performers, etc)
    }
    
    return render(request, 'branches/branch_product_report.html', context)
    
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
    """Company-wide aggregate financial report"""
    # Only Admin can access company-wide reports
    if request.user.profile.role != 'admin':
        return redirect('dashboard')
        
    date_range = request.GET.get('range', 'month')
    start_str = request.GET.get('start_date', '')
    end_str = request.GET.get('end_date', '')
    
    from branches.services.reporting import ReportingService
    reporting_service = ReportingService(tenant=request.user.profile.tenant, branch=None)
    
    start_date, end_date = reporting_service.get_date_range(date_range, start_str, end_str)
    
    # Get Analytics via Service
    company_summary = reporting_service.get_company_financial_summary(start_date, end_date)
    top_products = reporting_service.get_company_top_products(start_date, end_date, limit=10)
    stock_insights = reporting_service.get_company_stock_insights(limit=10)
    
    context = {
        'tenant': request.user.profile.tenant,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        
        # Financial and Product Analytics
        **company_summary,
        'top_products': top_products,
        **stock_insights
    }
    
    return render(request, 'branches/company_financial_report.html', context)

# LEGACY API ENDPOINTS REMOVED - Migrated to api/views.py OfflineSyncViewSet


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
    
    # Sent Transfers (Branch is the source)
    sent_transfers = StockTransfer.objects.filter(source_branch=branch).order_by('-created_at')
    
    # Received Transfers (Branch is the destination)
    received_transfers = StockTransfer.objects.filter(destination_branch=branch).order_by('-created_at')
    
    context = {
        'branch': branch,
        'sent_transfers': sent_transfers,
        'received_transfers': received_transfers,
        'title': 'Stock Transfers'
    }
    return render(request, 'branches/transfers/transfer_list.html', context)

@login_required
def transfer_create(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    products = Product.objects.filter(branch=branch, is_active=True, stock_quantity__gt=0)
    transfer_service = TransferService(tenant=request.user.profile.tenant, user_profile=request.user.profile)
    
    if request.method == 'POST':
        form = StockTransferForm(request.POST, user=request.user, branch_id=branch.id)
        if form.is_valid():
            try:
                items_data_str = request.POST.get('items_json')
                if not items_data_str:
                    raise Exception("No items selected")
                
                items_data = json.loads(items_data_str)
                destination_branch = form.cleaned_data['destination_branch']
                notes = form.cleaned_data['notes']
                
                transfer = transfer_service.request_transfer(
                    source_branch=branch,
                    destination_branch=destination_branch,
                    items_data=items_data,
                    notes=notes
                )
                
                messages.success(request, f"Transfer {transfer.reference_id} created successfully.")
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
    return render(request, 'branches/transfers/transfer_form.html', context)

@login_required
def transfer_request(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    source_branch_id = request.GET.get('source_branch')
    
    source_branch = None
    products = []
    if source_branch_id:
        source_branch = get_object_or_404(Branch, pk=source_branch_id, tenant=request.user.profile.tenant)
        products = Product.objects.filter(branch=source_branch, is_active=True, stock_quantity__gt=0)
    
    transfer_service = TransferService(tenant=request.user.profile.tenant, user_profile=request.user.profile)
    
    if request.method == 'POST':
        # In request mode, the current branch is the DESTINATION
        # and the selected source_branch_id is the SOURCE
        source_id = request.POST.get('source_branch_id')
        if not source_id:
            messages.error(request, "Please select a source branch first.")
            return redirect('transfer_request', branch_id=branch.id)
            
        source_branch = get_object_or_404(Branch, pk=source_id, tenant=request.user.profile.tenant)
        
        try:
            items_data_str = request.POST.get('items_json')
            if not items_data_str:
                raise Exception("No items requested")
            
            items_data = json.loads(items_data_str)
            notes = request.POST.get('notes')
            
            # Note: request_transfer takes (source, destination, items, notes)
            transfer = transfer_service.request_transfer(
                source_branch=source_branch,
                destination_branch=branch,
                items_data=items_data,
                notes=notes
            )
            
            messages.success(request, f"Stock request {transfer.reference_id} sent to {source_branch.name}.")
            return redirect('transfer_detail', branch_id=branch.id, pk=transfer.id)
            
        except Exception as e:
            messages.error(request, str(e))
    
    other_branches = Branch.objects.filter(tenant=request.user.profile.tenant).exclude(id=branch.id)
    
    context = {
        'branch': branch,
        'source_branch': source_branch,
        'other_branches': other_branches,
        'products': products,
        'title': 'Request Stock'
    }
    return render(request, 'branches/transfers/transfer_request_form.html', context)

@login_required
def transfer_detail(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    transfer = get_object_or_404(StockTransfer, pk=pk, tenant=request.user.profile.tenant)
    
    # RBAC: User must be in source or destination branch (or admin)
    user_branch_id = request.user.profile.branch.id if request.user.profile.branch else None
    if request.user.profile.role != 'admin':
         if user_branch_id not in [transfer.source_branch.id, transfer.destination_branch.id]:
             messages.error(request, "Permission denied: Access to this transfer is restricted.")
             return redirect('transfer_list', branch_id=branch.id)

    context = {
        'branch': branch,
        'transfer': transfer,
        'is_source': (branch.id == transfer.source_branch.id),
        'is_destination': (branch.id == transfer.destination_branch.id),
        'title': f'Transfer {transfer.reference_id}'
    }
    return render(request, 'branches/transfers/transfer_detail.html', context)

@login_required
def transfer_approve(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    transfer_service = TransferService(tenant=request.user.profile.tenant, user_profile=request.user.profile)
    
    if request.method == 'POST':
        result = transfer_service.approve_transfer(pk)
        if result['status'] == 'success':
            messages.success(request, "Transfer approved.")
        else:
            messages.error(request, result['message'])
            
    return redirect('transfer_detail', branch_id=branch.id, pk=pk)

@login_required
def transfer_ship(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    transfer_service = TransferService(tenant=request.user.profile.tenant, user_profile=request.user.profile)
    
    if request.method == 'POST':
        result = transfer_service.ship_transfer(pk)
        if result['status'] == 'success':
            messages.success(request, "Stock shipped from source branch.")
        else:
            messages.error(request, result['message'])
            
    return redirect('transfer_detail', branch_id=branch.id, pk=pk)

@login_required
def transfer_receive(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    transfer_service = TransferService(tenant=request.user.profile.tenant, user_profile=request.user.profile)
    
    if request.method == 'POST':
        result = transfer_service.receive_transfer(pk)
        if result['status'] == 'success':
            messages.success(request, "Transfer completed. Stock added to destination.")
        else:
            messages.error(request, result['message'])
            
    return redirect('transfer_detail', branch_id=branch.id, pk=pk)


# -----------------------------------------------------------------------------
# Purchase Order Views
# -----------------------------------------------------------------------------

from .models import Supplier, PurchaseOrder, PurchaseOrderItem
from .forms_po import SupplierForm, PurchaseOrderForm

@login_required
def supplier_list(request, branch_id):
    # Restrict access for sales role
    if request.user.profile.role == 'sales':
        return redirect('branch_dashboard', branch_id=branch_id)
    
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
    # Restrict access for sales role
    if request.user.profile.role == 'sales':
        return redirect('branch_dashboard', branch_id=branch_id)
    
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
    # Restrict access for sales role
    if request.user.profile.role == 'sales':
        return redirect('branch_dashboard', branch_id=branch_id)
    
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    products = Product.objects.filter(
        Q(branch=branch) | Q(branch__isnull=True),
        is_active=True,
        tenant=request.user.profile.tenant
    )
    
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, tenant=request.user.profile.tenant)
        if form.is_valid():
            items_data = request.POST.get('items_json')
            if not items_data:
                 messages.error(request, "No items selected")
            else:
                try:
                    items = json.loads(items_data)
                    from .services.purchase_orders import PurchaseOrderService
                    po_service = PurchaseOrderService(tenant=request.user.profile.tenant, user_profile=request.user.profile)
                    
                    result = po_service.create_po(
                        branch=branch,
                        supplier_id=form.cleaned_data['supplier'].id,
                        expected_date=form.cleaned_data['expected_date'],
                        items_data=items,
                        notes=form.cleaned_data.get('notes'),
                        amount_paid=form.cleaned_data.get('amount_paid') or 0,
                        payment_method=form.cleaned_data.get('payment_method') or 'cash'
                    )
                    
                    if result['status'] == 'success':
                        messages.success(request, f"Purchase Order {result['reference_id']} created successfully.")
                        return redirect('purchase_order_list', branch_id=branch_id)
                    else:
                        messages.error(request, f"Error: {result['message']}")
                except Exception as e:
                    messages.error(request, f"An error occurred: {str(e)}")
                # Stay on form page if error
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
    else:
        form = PurchaseOrderForm(tenant=request.user.profile.tenant)
        prefill_product_id = request.GET.get('product_id')
    
    context = {
        'branch': branch,
        'form': form,
        'products': products,
        'title': 'New Purchase Order',
        'prefill_product_id': prefill_product_id if request.method == 'GET' else None,
    }
    return render(request, 'branches/po_form.html', context)

# -----------------------------------------------------------------------------
# Branch Financials (Expenses, P&L, Tax)
# -----------------------------------------------------------------------------

@login_required
def branch_expense_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    from django.db.models.functions import Coalesce
    from decimal import Decimal
    
    # Get filter parameters
    category_id = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Base queryset - Filter by Branch
    expenses = Expense.objects.filter(branch=branch).select_related(
        'category', 'created_by'
    )
    
    # Apply filters
    if category_id:
        expenses = expenses.filter(category_id=category_id)
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    
    # Calculate summary statistics
    summary = expenses.aggregate(
        total_amount=Coalesce(Sum('amount'), Decimal('0.00')),
        expense_count=Count('id')
    )
    
    # Category breakdown
    category_breakdown = expenses.values('category__name', 'category__type').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Get filter options
    categories = ExpenseCategory.objects.filter(tenant=branch.tenant)
    
    context = {
        'branch': branch,
        'expenses': expenses,
        'summary': summary,
        'category_breakdown': category_breakdown,
        'categories': categories,
        'filters': {
            'category': category_id,
            'start_date': start_date,
            'end_date': end_date,
        },
        'title': 'Branch Expenses'
    }
    return render(request, 'branches/expense_list.html', context)

@login_required
def branch_expense_create(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, tenant=branch.tenant)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.tenant = branch.tenant
            expense.branch = branch  # Force branch assignment
            expense.created_by = request.user.profile
            expense.save()
            messages.success(request, 'Expense recorded successfully!')
            return redirect('branch_expense_list', branch_id=branch.id)
    else:
        form = ExpenseForm(tenant=branch.tenant)
        # We can optionally preset the branch if the form allows it, 
        # but usually ExpenseForm might have a branch dropdown.
        # Since we are in a branch context, we should probably hide/disable branch selection 
        # or just ensure it's saved to this branch in the backend (which we do above).
    
    context = {
        'branch': branch,
        'form': form,
        'title': 'Add Expense'
    }
    return render(request, 'branches/expense_form.html', context)

@login_required
def branch_expense_update(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    expense = get_object_or_404(Expense, pk=pk, branch=branch)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense, tenant=branch.tenant)
        if form.is_valid():
            # Ensure branch stays same even if form has branch field
            obj = form.save(commit=False)
            obj.branch = branch
            obj.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('branch_expense_list', branch_id=branch.id)
    else:
        form = ExpenseForm(instance=expense, tenant=branch.tenant)
    
    context = {
        'branch': branch,
        'form': form,
        'expense': expense,
        'title': 'Edit Expense'
    }
    return render(request, 'branches/expense_form.html', context)

@login_required
def branch_expense_delete(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    expense = get_object_or_404(Expense, pk=pk, branch=branch)
    
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('branch_expense_list', branch_id=branch.id)
    
    context = {
        'branch': branch,
        'expense': expense,
        'title': 'Delete Expense'
    }
    return render(request, 'branches/expense_confirm_delete.html', context)

@login_required
def branch_profit_loss_report(request, branch_id):
    from django.db.models.functions import Coalesce, TruncDate
    from decimal import Decimal
    from datetime import datetime, timedelta
    
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    # Date range filtering
    date_range = request.GET.get('range', 'month')
    today = timezone.now().date()
    
    if date_range == 'today':
        start_date = today
        end_date = today
    elif date_range == 'week':
        start_date = today - timedelta(days=7)
        end_date = today
    elif date_range == 'month':
        start_date = today - timedelta(days=30)
        end_date = today
    elif date_range == 'year':
        start_date = today - timedelta(days=365)
        end_date = today
    elif date_range == 'custom':
        start_date = request.GET.get('start_date', today - timedelta(days=30))
        end_date = request.GET.get('end_date', today)
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:  # all
        start_date = None
        end_date = None
    
    # Revenue calculations (Branch specific)
    orders_query = Order.objects.filter(branch=branch, status='completed')
    if start_date and end_date:
        orders_query = orders_query.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
    
    revenue_data = orders_query.aggregate(
        total_revenue=Coalesce(Sum('total_amount'), Decimal('0.00')),
        total_tax=Coalesce(Sum('tax_amount'), Decimal('0.00')),
        order_count=Count('id')
    )
    
    # Calculate cost of goods sold (COGS)
    order_items = OrderItem.objects.filter(order__in=orders_query)
    cogs = order_items.aggregate(
        total_cogs=Coalesce(Sum(models.F('quantity') * models.F('cost_price'), output_field=models.DecimalField()), Decimal('0.00'))
    )['total_cogs']
    
    # Gross profit
    gross_revenue = revenue_data['total_revenue'] - revenue_data['total_tax']
    gross_profit = gross_revenue - cogs
    gross_margin = (gross_profit / gross_revenue * 100) if gross_revenue > 0 else 0
    
    # Expense calculations (Branch specific)
    expenses_query = Expense.objects.filter(branch=branch)
    if start_date and end_date:
        expenses_query = expenses_query.filter(date__gte=start_date, date__lte=end_date)
    
    expense_data = expenses_query.aggregate(
        total_expenses=Coalesce(Sum('amount'), Decimal('0.00'))
    )
    
    # Expense breakdown by category
    expense_breakdown = expenses_query.values('category__name', 'category__type').annotate(
        amount=Sum('amount')
    ).order_by('-amount')
    
    # Net profit
    net_profit = gross_profit - expense_data['total_expenses']
    net_margin = (net_profit / gross_revenue * 100) if gross_revenue > 0 else 0
    
    # Revenue trend (daily for the period)
    if start_date and end_date:
        revenue_trend = orders_query.annotate(
            day=TruncDate('created_at')
        ).values('day').annotate(
            revenue=Sum('total_amount')
        ).order_by('day')
    else:
        revenue_trend = []
    
    context = {
        'branch': branch,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        'revenue_data': revenue_data,
        'gross_revenue': gross_revenue,
        'cogs': cogs,
        'gross_profit': gross_profit,
        'gross_margin': gross_margin,
        'expense_data': expense_data,
        'expense_breakdown': expense_breakdown,
        'net_profit': net_profit,
        'net_margin': net_margin,
        'revenue_trend': revenue_trend,
        'title': 'Profit & Loss Statement'
    }
    return render(request, 'branches/profit_loss_report.html', context)

@login_required
def branch_tax_report(request, branch_id):
    from django.db.models.functions import Coalesce, TruncDate
    from decimal import Decimal
    from datetime import datetime, timedelta
    
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    # Get tax configuration
    try:
        tax_config = TaxConfiguration.objects.get(tenant=branch.tenant)
    except TaxConfiguration.DoesNotExist:
        # Just use a dummy one or None, template handles None
        tax_config = None
    
    # Date range filtering
    date_range = request.GET.get('range', 'month')
    today = timezone.now().date()
    
    if date_range == 'today':
        start_date = today
        end_date = today
    elif date_range == 'week':
        start_date = today - timedelta(days=7)
        end_date = today
    elif date_range == 'month':
        start_date = today - timedelta(days=30)
        end_date = today
    elif date_range == 'quarter':
        start_date = today - timedelta(days=90)
        end_date = today
    elif date_range == 'year':
        start_date = today - timedelta(days=365)
        end_date = today
    elif date_range == 'custom':
        start_date = request.GET.get('start_date', today - timedelta(days=30))
        end_date = request.GET.get('end_date', today)
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        start_date = None
        end_date = None
    
    # Get completed orders (Branch specific)
    orders_query = Order.objects.filter(branch=branch, status='completed')
    if start_date and end_date:
        orders_query = orders_query.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
    
    # Tax calculations
    tax_summary = orders_query.aggregate(
        total_sales=Coalesce(Sum('total_amount'), Decimal('0.00')),
        total_tax_collected=Coalesce(Sum('tax_amount'), Decimal('0.00')),
        taxable_amount=Coalesce(Sum('subtotal'), Decimal('0.00')),
        order_count=Count('id')
    )
    
    # Daily tax collection
    if start_date and end_date:
        daily_tax = orders_query.annotate(
            day=TruncDate('created_at')
        ).values('day').annotate(
            tax=Sum('tax_amount'),
            sales=Sum('total_amount')
        ).order_by('day')
    else:
        daily_tax = []
    
    context = {
        'branch': branch,
        'tax_config': tax_config,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        'tax_summary': tax_summary,
        'daily_tax': daily_tax,
        'title': 'Tax Report'
    }
    return render(request, 'branches/tax_report.html', context)

@login_required
def purchase_order_detail(request, branch_id, pk):
    # Restrict access for sales role
    if request.user.profile.role == 'sales':
        return redirect('branch_dashboard', branch_id=branch_id)
    
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
    # Restrict access for sales role
    if request.user.profile.role == 'sales':
        return redirect('branch_dashboard', branch_id=branch_id)
    
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

@login_required
def gift_card_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    gift_cards = GiftCard.objects.filter(tenant=request.user.profile.tenant).order_by('-created_at')
    
    return render(request, 'branches/gift_card_list.html', {
        'branch': branch,
        'gift_cards': gift_cards,
        'title': 'Gift Cards'
    })

@login_required
def gift_card_create(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    # Restrict: Sales can't create gift cards
    if request.user.profile.role == 'sales':
        messages.error(request, 'Permission Denied: Sales staff cannot create gift cards.')
        return redirect('gift_card_list', branch_id=branch.id)
    
    if request.method == 'POST':
        form = GiftCardForm(request.POST)
        if form.is_valid():
            gift_card = form.save(commit=False)
            gift_card.tenant = request.user.profile.tenant
            # Link to a customer if provided? For now, independent.
            gift_card.save()
            messages.success(request, 'Gift Card created successfully.')
            return redirect('gift_card_list', branch_id=branch.id)
    else:
        form = GiftCardForm()
    
    return render(request, 'branches/gift_card_form.html', {
        'branch': branch,
        'form': form,
        'title': 'Create Gift Card'
    })

# Employee Management Views

@login_required
def attendance_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    if request.user.profile.role in ['admin', 'manager']:
        # Show all records for the branch
        attendance_records = Attendance.objects.filter(branch=branch).select_related('user', 'user__user').order_by('-clock_in')
        title = 'Staff Attendance'
    else:
        # Show only own records
        attendance_records = Attendance.objects.filter(user=request.user.profile).order_by('-clock_in')
        title = 'My Attendance'
    
    # Check if currently clocked in (Always check for the logged in user)
    current_session = Attendance.objects.filter(user=request.user.profile, clock_out__isnull=True).first()
    
    return render(request, 'branches/attendance_list.html', {
        'branch': branch,
        'attendance_records': attendance_records,
        'current_session': current_session,
        'title': title
    })

@login_required
def clock_in(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    if request.method == 'POST':
        # Check if already clocked in
        if Attendance.objects.filter(user=request.user.profile, branch=branch, clock_out__isnull=True).exists():
            messages.warning(request, 'You are already clocked in.')
        else:
            Attendance.objects.create(user=request.user.profile, branch=branch)
            messages.success(request, 'Clocked in successfully.')
    return redirect('attendance_list', branch_id=branch.id)

@login_required
def clock_out(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    if request.method == 'POST':
        # Find active session
        session = Attendance.objects.filter(user=request.user.profile, branch=branch, clock_out__isnull=True).last()
        if session:
            session.clock_out = timezone.now()
            session.save()
            messages.success(request, 'Clocked out successfully.')
        else:
            messages.warning(request, 'You are not clocked in.')
    return redirect('attendance_list', branch_id=branch.id)

@login_required
def staff_performance_report(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    # Only Managers/Admins should view full report? Or open to all? 
    # Let's say open to all for now, or restrict.
    # user_role = request.user.profile.role
    
    # Aggregate sales by cashier
    # Ensure to only count completed orders
    performance_data = UserProfile.objects.filter(tenant=request.user.profile.tenant).annotate(
        total_orders=Count('processed_orders', filter=models.Q(processed_orders__branch=branch, processed_orders__status='completed')),
        total_sales=Sum('processed_orders__total_amount', filter=models.Q(processed_orders__branch=branch, processed_orders__status='completed'))
    ).filter(total_orders__gt=0).order_by('-total_sales')
    
    return render(request, 'branches/staff_performance.html', {
        'branch': branch,
        'performance_data': performance_data,
        'title': 'Staff Performance'
    })

@login_required
def void_order(request, branch_id, order_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    order = get_object_or_404(Order, pk=order_id, branch=branch)
    
    # RBAC: Only Admin or Manager can void
    if request.user.profile.role not in ['admin', 'manager']:
        messages.error(request, 'Permission denied: Only Managers can void orders.')
        return redirect('transaction_detail', branch_id=branch.id, order_id=order.id)
        
    if request.method == 'POST':
        from .services.pos import POSService
        service = POSService(tenant=request.user.profile.tenant, user_profile=request.user.profile)
        result = service.void_order(order_id)
        
        if result['status'] == 'success':
            messages.success(request, result['message'])
        elif result['status'] == 'info':
            messages.info(request, result['message'])
        else:
            messages.error(request, result['message'])
            
    return redirect('transaction_detail', branch_id=branch.id, order_id=order.id)

@login_required
def complete_order(request, branch_id, order_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    order = get_object_or_404(Order, pk=order_id, branch=branch)
    
    if request.method == 'POST':
        from .services.pos import POSService
        service = POSService(tenant=request.user.profile.tenant, user_profile=request.user.profile)
        result = service.complete_pending_order(order_id)
        
        if result['status'] == 'success':
            messages.success(request, result['message'])
        else:
            messages.error(request, result['message'])
            
    return redirect('transaction_detail', branch_id=branch.id, order_id=order.id)

# Analytics Views

@login_required
def analytics_dashboard(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    # Date Filtering
    date_start = request.GET.get('date_start', '')
    date_end = request.GET.get('date_end', '')
    
    orders = Order.objects.filter(branch=branch, status='completed')
    
    if date_start:
        orders = orders.filter(created_at__date__gte=date_start)
    if date_end:
        orders = orders.filter(created_at__date__lte=date_end)
        
    # Aggegate Data
    
    # 1. Sales Over Time (Busiest Hours/Days) - Simplified to daily total for line chart
    # Group by date
    from django.db.models.functions import TruncDate
    sales_over_time = orders.annotate(date=TruncDate('created_at')).values('date').annotate(total=Sum('total_amount')).order_by('date')
    
    # 2. Top Selling Categories
    # Join OrderItems -> Product -> Category
    category_sales = OrderItem.objects.filter(order__in=orders).values('product__category__name').annotate(total_sales=Sum(models.F('price') * models.F('quantity')), total_qty=Sum('quantity')).order_by('-total_sales')[:5]
    
    # 3. Profit Analysis
    # Profit = (Price - Cost) * Quantity
    # We need to calculate this carefully.
    total_sales = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Calculate total cost
    # Warning: This assumes cost_price is populated on OrderItem. If historic data is missing cost, it counts as 0 cost (100% margin).
    total_cost = OrderItem.objects.filter(order__in=orders).aggregate(
        cost=Sum(models.F('cost_price') * models.F('quantity'))
    )['cost'] or 0
    
    gross_profit = total_sales - total_cost
    margin = (gross_profit / total_sales * 100) if total_sales > 0 else 0
    
    # Prepare chart data for template
    chart_dates = [entry['date'].strftime('%Y-%m-%d') for entry in sales_over_time]
    chart_sales = [float(entry['total']) for entry in sales_over_time]
    
    cat_names = [entry['product__category__name'] or 'Uncategorized' for entry in category_sales]
    cat_values = [float(entry['total_sales']) for entry in category_sales]
    
    context = {
        'branch': branch,
        'title': 'Analytics Dashboard',
        'total_sales': total_sales,
        'total_cost': total_cost,
        'gross_profit': gross_profit,
        'margin': margin,
        'chart_dates': json.dumps(chart_dates),
        'chart_sales': json.dumps(chart_sales),
        'cat_names': json.dumps(cat_names),
        'cat_values': json.dumps(cat_values),
        'date_start': date_start,
        'date_end': date_end
    }
    
    return render(request, 'branches/analytics_dashboard.html', context)

@login_required
def export_sales_csv(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{branch.name}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Date', 'Customer', 'Cashier', 'Status', 'Total', 'Payment Method'])
    
    orders = Order.objects.filter(branch=branch).order_by('-created_at')
    
    for order in orders:
        writer.writerow([
            order.id,
            order.created_at.strftime('%Y-%m-%d %H:%M'),
            order.customer.name if order.customer else 'Guest',
            order.cashier.user.username if order.cashier else 'Unknown',
            order.status,
            order.total_amount,
            order.get_payment_method_display()
        ])
        
    return response
@require_api_key_django
def validate_pos_pin(request, branch_id):
    """
    Validates a staff PIN and returns user data for POS switching.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
        
    try:
        data = json.loads(request.body)
        pin = data.get('pin')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        
    if not pin:
        return JsonResponse({'success': False, 'error': 'PIN required'}, status=400)
        
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.tenant)
    
    # We cannot filter by pos_pin in the DB because it's an EncryptedTextField
    # Fetch all user profiles for this tenant and check the PIN in Python
    profiles = UserProfile.objects.filter(tenant=request.tenant)
    profile = None
    
    for p in profiles:
        if p.pos_pin == pin:
            profile = p
            break
    
    if not profile:
        return JsonResponse({'success': False, 'error': 'Invalid PIN'}, status=401)
        
    # Perform account switch in Django session
    if request.user.id != profile.user.id:
        # Save current tenant context
        tenant = getattr(request, 'tenant', None)
        
        # Log out previous user and log in new user
        logout(request)
        login(request, profile.user, backend='django.contrib.auth.backends.ModelBackend')
        
        # Restore tenant context (though TenantMiddleware should re-attach it)
        if tenant:
            request.tenant = tenant
            
    # Get the tenant's API key if it exists
    pos_api_key = request.tenant.pos_api_key
    
    return JsonResponse({
        'success': True,
        'user': {
            'id': str(profile.user.id),
            'name': profile.user.get_full_name() or profile.user.username,
            'username': profile.user.username,
            'role': profile.role
        },
        'api_key': pos_api_key
    })
