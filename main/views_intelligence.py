from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import datetime
from main.models import Product, Order
from accounts.models import Branch
from .services.intelligence_service import IntelligenceService

@login_required
def inventory_forecast_view(request, branch_id=None):
    """
    Full page view for inventory forecasting.
    Includes filtering capabilities and full list.
    """
    profile = request.user.profile
    if profile.role in ['sales']:
        return redirect('dashboard')
        
    tenant = profile.tenant
    branch = None
    
    # Base filter for active products
    products = Product.objects.filter(
        tenant=tenant, 
        is_active=True,
    ).select_related('category')
    
    if branch_id:
        branch = get_object_or_404(Branch, id=branch_id, tenant=tenant)
        products = products.filter(branch=branch)

    # Calculate metrics in Python (as per widget logic)
    forecasts = []
    for p in products:
        if p.stock_quantity <= 0:
            continue
            
        days = p.get_days_until_stockout()
        velocity = p.get_daily_sales_velocity()
        
        # We can add a "status" for the UI
        status = 'healthy'
        if days < 7:
            status = 'critical'
        elif days < 30:
            status = 'warning'
            
        forecasts.append({
            'product': p,
            'days_left': days,
            'velocity': velocity,
            'status': status
        })
    
    # Sort by days left (ascending)
    forecasts.sort(key=lambda x: x['days_left'])
    
    return render(request, 'main/intelligence/inventory_forecast.html', {
        'forecasts': forecasts,
        'branch': branch,
        'page_title': 'Inventory Intelligence'
    })

@login_required
def generate_auto_pos_api(request, branch_id=None):
    """
    API/Action view to trigger automatic PO generation.
    """
    profile = request.user.profile
    if profile.role in ['sales']:
        return JsonResponse({'error': 'Permission denied'}, status=403)
        
    tenant = profile.tenant
    branch = None
    if branch_id:
        branch = get_object_or_404(Branch, id=branch_id, tenant=tenant)
        
    service = IntelligenceService(tenant, branch)
    pos = service.generate_auto_pos(request.user.profile)
    
    if pos:
        messages.success(request, f"Successfully generated {len(pos)} draft Purchase Orders.")
    else:
        messages.info(request, "No products met the criteria for automatic replenishment at this time.")
        
    if branch:
        return redirect('inventory_forecast_branch', branch_id=branch.id)
    return redirect('inventory_forecast')

from api.auth import require_api_key_django

@csrf_exempt
@require_api_key_django
def get_pos_recommendations(request):
    """
    API for POS to get frequently bought together suggestions.
    Expects GET with product_ids (comma separated) or single product_id.
    """
    try:
        if request.method != 'GET':
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        
        # Validation for Profile
        profile = getattr(request.user, 'profile', None)
        if not profile:
             import logging
             logger = logging.getLogger(__name__)
             logger.error(f"User {request.user} has no profile attached for POS recommendations")
             return JsonResponse({'error': 'User profile not found. Please re-login.'}, status=401)

        product_ids = request.GET.get('product_ids', '').split(',')
        product_ids = [pid.strip() for pid in product_ids if pid.strip()]
        
        if not product_ids:
            return JsonResponse({'recommendations': []})
        
        service = IntelligenceService(tenant=request.user.profile.tenant)
        all_recoms = []
        seen_ids = set(product_ids)
        
        for pid in product_ids:
            try:
                # Handle invalid UUIDs gracefully
                try:
                    product = Product.objects.get(id=pid, tenant=request.user.profile.tenant)
                except (Product.DoesNotExist, ValueError, TypeError):
                    continue
                    
                recoms = service.get_frequently_bought_together(product, limit=3)
                for r in recoms:
                    if str(r.id) not in seen_ids:
                        all_recoms.append({
                            'id': str(r.id),
                            'name': r.name,
                            'price': float(r.price),
                            'image_url': r.image_url,
                            'sku': r.sku
                        })
                        seen_ids.add(str(r.id))
            except Exception as e:
                print(f"Error processing product {pid}: {e}")
                continue
                
        return JsonResponse({'recommendations': all_recoms[:6]})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def staff_leaderboard_view(request, branch_id=None):
    """
    Full page view for staff performance.
    """
    profile = request.user.profile
    if profile.role in ['sales']:
        return redirect('dashboard')
        
    tenant = profile.tenant
    
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - datetime.timedelta(days=days)
    
    orders = Order.objects.filter(
        tenant=tenant,
        status='completed',
        created_at__gte=start_date,
        cashier__isnull=False
    )
    
    branch = None
    if branch_id:
        branch = get_object_or_404(Branch, id=branch_id, tenant=tenant)
        orders = orders.filter(branch=branch)
        
    leaderboard = orders.values(
        'cashier__user__first_name', 
        'cashier__user__last_name', 
        'cashier__user__username',
        'cashier__id'
    ).annotate(
        total_sales=Sum('total_amount'),
        orders_count=Count('id')
    ).order_by('-total_sales')
    
    return render(request, 'main/intelligence/staff_leaderboard.html', {
        'leaderboard': leaderboard,
        'days': days,
        'branch': branch,
        'page_title': 'Staff Performance'
    })
