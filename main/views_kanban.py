from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Order
from accounts.models import Branch, UserProfile

@login_required
def order_kanban_redirect(request):
    """Redirect generic kanban to the first available branch"""
    tenant = request.user.profile.tenant
    first_branch = Branch.objects.filter(tenant=tenant).first()
    
    if not first_branch:
        from django.contrib import messages
        messages.warning(request, "Please create at least one branch to use the Kanban board.")
        return redirect('dashboard')
        
    return redirect('order_kanban_branch', branch_id=first_branch.id)

@login_required
def order_kanban(request, branch_id):
    """Render the Kanban board for orders"""
    tenant = request.user.profile.tenant

    
    # Fetch active orders (exclude cancelled if desired, but keep completed for a bit?)
    # Usually Kanban shows recent completed.
    
    # We'll fetch all orders from last 24h OR active status
    from django.db.models import Q
    import datetime
    
    cutoff = timezone.now() - datetime.timedelta(hours=24)
    
    orders = Order.objects.filter(
        Q(status__in=['pending', 'processing', 'ready']) | 
        Q(status='completed', updated_at__gte=cutoff),
        tenant=tenant
    ).select_related('customer', 'branch').order_by('-created_at')
    
    branch = get_object_or_404(Branch, id=branch_id, tenant=tenant)
    orders = orders.filter(branch=branch)
    
    # Group by status
    columns = {
        'pending': [],
        'processing': [],
        'ready': [],
        'completed': []
    }
    
    for order in orders:
        if order.status in columns:
            columns[order.status].append(order)
            
    return render(request, 'main/kanban.html', {
        'columns': columns,
        'page_title': 'Kitchen Display System (Kanban)',
        'branch': branch
    })

@login_required
@require_POST
def update_order_status_api(request, branch_id):
    """API to update order status via drag-and-drop"""
    try:
        import json
        data = json.loads(request.body)
        order_id = data.get('order_id')
        new_status = data.get('status')
        
        print(f"[Kanban] Received status update request: order_id={order_id}, new_status={new_status}")
        
        if new_status not in ['pending', 'processing', 'ready', 'completed', 'cancelled']:
            return JsonResponse({'error': 'Invalid status'}, status=400)
            
        tenant = request.user.profile.tenant
        order = get_object_or_404(Order, id=order_id, tenant=tenant, branch_id=branch_id)
        
        old_status = order.status
        print(f"[Kanban] Order {order.order_number}: {old_status} -> {new_status}")
        print(f"[Kanban] Order customer: {order.customer}")
        if order.customer:
            print(f"[Kanban] Customer email: {order.customer.email}")
        
        order.status = new_status
        order.save()
        
        # Trigger Notification Signal if needed (Already handled by post_save logic if implemented)
        if old_status != new_status:
            print(f"[Kanban] Status changed, attempting to side effects...")
            
            # 1. Handle Cashier Assignment & Stock Deduction upon Completion
            if new_status == 'completed':
                # Assign the staff moving the card as the cashier
                order.cashier = request.user.profile
                
                # Check for stock deduction
                # Online orders deduct stock at CREATION (storefront/views.py)
                # Other orders (Kiosk, POS, etc.) deduct stock when they become 'completed'
                if order.ordering_type != 'online':
                    from branches.services.pos import POSService
                    pos_service = POSService(tenant=tenant, user_profile=request.user.profile)
                    for item in order.items.all():
                        if item.product:
                            pos_service._deduct_stock(item.product, item.quantity, order, order.branch)
                    print(f"[Kanban] Stock deducted for {order.ordering_type} order {order.order_number}")
                else:
                    print(f"[Kanban] Skipping stock deduction for Online order (already handled at creation)")
                
                order.save()

            # 2. Trigger Notification Email
            try:
                from notifications.utils import send_order_status_email_to_customer
                send_order_status_email_to_customer(order)
                print(f"[Kanban] Email function completed")
            except Exception as e:
                print(f"[Kanban] Failed to send email: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"[Kanban] Status unchanged, skipping side effects")
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Order {order.order_number} moved to {new_status}'
        })
        
    except Exception as e:
        print(f"[Kanban] Error in update_order_status_api: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
