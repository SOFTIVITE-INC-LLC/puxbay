from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Q
from django.utils import timezone
from datetime import timedelta
from main.models import Product
from .models import StockBatch, StockMovement, Branch
from .forms import StockReceiveForm
from accounts.models import UserProfile

@login_required
def inventory_dashboard(request, branch_id):
    try:
        profile = request.user.profile
        # If user has a branch assigned, ensure they are accessing their own branch
        if profile.branch and str(profile.branch.id) != str(branch_id) and profile.role != 'admin':
             return redirect('branch_dashboard', branch_id=profile.branch.id)
        # If user has NO branch but isn't admin (edge case?), revert to safety
        elif not profile.branch and profile.role != 'admin':
             return redirect('landing')
    except UserProfile.DoesNotExist:
        return redirect('landing')

    today = timezone.now().date()
    seven_days = today + timedelta(days=7)
    thirty_days = today + timedelta(days=30)

    # Low Stock Products (based on reorder_quantity or arbitrary threshold)
    low_stock_products = Product.objects.filter(
        branch__id=branch_id, 
        stock_quantity__lte=F('low_stock_threshold')
    )[:10]

    # Expiring Batches
    expiring_batches = list(StockBatch.objects.filter(
        branch__id=branch_id,
        expiry_date__range=[today, thirty_days],
        quantity__gt=0
    ))
    
    # Expiring Products (which are NOT batch tracked but have expiry dates)
    expiring_products = Product.objects.filter(
        branch__id=branch_id,
        expiry_date__range=[today, thirty_days],
        stock_quantity__gt=0,
        is_batch_tracked=False
    )
    
    # Combine and standardize
    combined_expiring = []
    
    # Add batches
    combined_expiring.extend(expiring_batches)
    
    # Add products wrapped to look like batches
    class ProductBatchWrapper:
        def __init__(self, product):
            self.product = product
            self.batch_number = product.batch_number if product.batch_number else "N/A"
            self.expiry_date = product.expiry_date
            self.quantity = product.stock_quantity
            
    for p in expiring_products:
        combined_expiring.append(ProductBatchWrapper(p))
        
    # Sort combined list by expiry date
    combined_expiring.sort(key=lambda x: x.expiry_date if x.expiry_date else timezone.now().date())
    
    # Slice top 10
    expiring_soon = combined_expiring[:10]
    
    # Same logic for EXPIRED items
    expired_batches_list = list(StockBatch.objects.filter(
        branch__id=branch_id,
        expiry_date__lt=today,
        quantity__gt=0
    ))
    
    expired_products = Product.objects.filter(
        branch__id=branch_id,
        expiry_date__lt=today,
        stock_quantity__gt=0,
        is_batch_tracked=False
    )
    
    combined_expired = []
    combined_expired.extend(expired_batches_list)
    for p in expired_products:
        combined_expired.append(ProductBatchWrapper(p))
        
    combined_expired.sort(key=lambda x: x.expiry_date if x.expiry_date else timezone.now().date())
    expired_batches = combined_expired[:10]

    branch = get_object_or_404(Branch, pk=branch_id)
    
    context = {
        'branch': branch,
        'branch_id': branch_id,
        'low_stock_products': low_stock_products,
        'expiring_soon': expiring_soon,
        'expired_batches': expired_batches,
        'title': 'Inventory Dashboard'
    }
    return render(request, 'branches/inventory/dashboard.html', context)

@login_required
def stock_movement_list(request, branch_id):
    movements = StockMovement.objects.filter(branch__id=branch_id).order_by('-created_at')[:50]
    return render(request, 'branches/inventory/movement_list.html', {
        'movements': movements, 
        'branch_id': branch_id,
        'title': 'Stock Audit Trail'
    })


@login_required
def stock_receive(request, branch_id):
    try:
        profile = request.user.profile
        if profile.branch and str(profile.branch.id) != str(branch_id) and profile.role != 'admin':
             return redirect('branch_dashboard', branch_id=profile.branch.id)
    except UserProfile.DoesNotExist:
        return redirect('landing')

    branch = get_object_or_404(Branch, pk=branch_id)
    products = Product.objects.filter(branch=branch)

    if request.method == 'POST':
        form = StockReceiveForm(request.POST, tenant=profile.tenant, branch=branch)
        if form.is_valid():
            product = form.cleaned_data['product']
            batch_number = form.cleaned_data['batch_number']
            expiry_date = form.cleaned_data['expiry_date']
            quantity = form.cleaned_data['quantity']
            cost_price = form.cleaned_data['cost_price']
            
            # Update or Create Batch
            batch, created = StockBatch.objects.get_or_create(
                branch=branch,
                product=product,
                batch_number=batch_number,
                defaults={
                    'tenant': branch.tenant,
                    'quantity': 0,
                    'expiry_date': expiry_date,
                    'cost_price': cost_price if cost_price else 0
                }
            )
            
            if not created:
                 if expiry_date: batch.expiry_date = expiry_date
                 if cost_price: batch.cost_price = cost_price
            
            batch.quantity += quantity
            batch.save()
            
            product.stock_quantity += quantity
            product.save()
            
            StockMovement.objects.create(
                tenant=branch.tenant,
                branch=branch,
                product=product,
                batch=batch,
                quantity_change=quantity,
                balance_after=product.stock_quantity,
                movement_type='receive',
                created_by=profile,
                notes=f"Received batch {batch_number}"
            )
            
            messages.success(request, f"Successfully received {quantity} of {product.name}")
            return redirect('inventory_dashboard', branch_id=branch_id)
    else:
        form = StockReceiveForm(tenant=profile.tenant, branch=branch)

    return render(request, 'branches/inventory/receive_form.html', {
        'branch': branch,
        'form': form, 
        'title': 'Receive Stock'
    })

@login_required
def batch_list(request, branch_id):
    try:
        profile = request.user.profile
        if profile.branch and str(profile.branch.id) != str(branch_id) and profile.role != 'admin':
             return redirect('branch_dashboard', branch_id=profile.branch.id)
    except UserProfile.DoesNotExist:
        return redirect('landing')

    branch = get_object_or_404(Branch, pk=branch_id)
    
    # 1. Fetch Batches
    batches_qs = StockBatch.objects.filter(branch=branch).order_by('expiry_date')
    
    # 2. Fetch Non-Batch Products with Expiry
    products_qs = Product.objects.filter(
        branch=branch, 
        is_batch_tracked=False,
        stock_quantity__gt=0
    )
    
    # Filter by product if needed
    product_id = request.GET.get('product')
    if product_id:
        batches_qs = batches_qs.filter(product_id=product_id)
        products_qs = products_qs.filter(id=product_id)
        
    # Filter for Expiring Soon/Expired
    filter_type = request.GET.get('filter')
    if filter_type == 'expiring':
        today = timezone.now().date()
        thirty_days = today + timedelta(days=30)
        batches_qs = batches_qs.filter(expiry_date__range=[today, thirty_days])
        products_qs = products_qs.filter(expiry_date__range=[today, thirty_days])
    elif filter_type == 'expired':
        today = timezone.now().date()
        batches_qs = batches_qs.filter(expiry_date__lt=today)
        products_qs = products_qs.filter(expiry_date__lt=today)

    # Wrapper class (redefined here for simplicity)
    class ProductBatchWrapper:
        def __init__(self, product):
            self.product = product
            self.batch_number = product.batch_number if product.batch_number else "N/A"
            self.expiry_date = product.expiry_date
            self.quantity = product.stock_quantity
            # Add other fields expected by template if any
            self.id = product.id # Fallback usage
            
    # Combine
    combined_list = list(batches_qs)
    for p in products_qs:
        # Only include if it has an expiry date set
        if p.expiry_date:
            combined_list.append(ProductBatchWrapper(p))
            
    # Sort
    combined_list.sort(key=lambda x: x.expiry_date if x.expiry_date else timezone.now().date())

    context = {
        'branch': branch,
        'batches': combined_list,
        'title': 'Batch Management'
    }
    return render(request, 'branches/inventory/batch_list.html', context)
