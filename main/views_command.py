from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q
from django.contrib import messages
from .models import Order, Product
from accounts.models import Branch
from decimal import Decimal

@login_required
def command_center(request):
    """Enterprise view comparing all branches side-by-side"""
    tenant = request.user.profile.tenant
    
    # Check if admin
    if request.user.profile.role != 'admin':
        messages.error(request, "Access denied. Only administrators can access the Command Center.")
        return redirect('dashboard')
    
    # Aggregate metrics by branch
    branch_metrics = Branch.objects.filter(tenant=tenant).annotate(
        total_revenue=Sum('orders__total_amount', filter=Q(orders__status='completed')),
        transaction_count=Count('orders', filter=Q(orders__status='completed')),
        avg_order_value=Avg('orders__total_amount', filter=Q(orders__status='completed'))
    ).order_by('-total_revenue')
    
    # Calculate global totals
    global_stats = {
        'revenue': sum(b.total_revenue or 0 for b in branch_metrics),
        'transactions': sum(b.transaction_count or 0 for b in branch_metrics),
    }
    
    return render(request, 'main/command_center.html', {
        'branch_metrics': branch_metrics,
        'global_stats': global_stats,
        'page_title': 'Command Center'
    })

@login_required
def global_price_update(request):
    """Allow updating prices for a specific SKU across all branches"""
    tenant = request.user.profile.tenant
    
    if request.user.profile.role != 'admin':
        messages.error(request, "Access denied.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        sku = request.POST.get('sku')
        new_price = request.POST.get('new_price')
        
        if not sku or not new_price:
            messages.error(request, "SKU and Price are required.")
        else:
            try:
                # Trigger background task
                from main.tasks import sync_global_prices_task
                sync_global_prices_task.delay(str(tenant.id), sku, new_price)
                
                messages.success(request, f"Global price update for SKU: {sku} has been queued. You will be notified upon completion.")
                return redirect('command_center')
                
            except Exception as e:
                messages.error(request, f"Update failed: {str(e)}")
                
    return render(request, 'main/global_price_update.html', {
        'page_title': 'Global Price Sync'
    })
