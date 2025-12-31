from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from branches.models import PurchaseOrder, PurchaseOrderItem
from main.models import Product, SupplierCreditTransaction
from django.db.models import Sum
import datetime

def is_supplier(user):
    return user.is_authenticated and user.profile.role == 'supplier'

@login_required
@user_passes_test(is_supplier)
def supplier_dashboard(request):
    """Supplier's main overview page"""
    try:
        supplier = request.user.profile.supplier_link.supplier
    except AttributeError:
        messages.error(request, "Your profile is not linked to any supplier.")
        return redirect('dashboard')
        
    tenant = request.user.profile.tenant
    
    # Active POs
    active_pos = PurchaseOrder.objects.filter(
        supplier=supplier,
        status__in=['draft', 'ordered']
    ).order_by('-created_at')
    
    # Recent Credit History
    credit_history = SupplierCreditTransaction.objects.filter(supplier=supplier).order_by('-created_at')[:5]
    
    context = {
        'supplier': supplier,
        'active_pos': active_pos,
        'credit_history': credit_history,
        'total_pending_amount': active_pos.filter(status='ordered').aggregate(total=Sum('total_cost'))['total'] or 0
    }
    return render(request, 'main/supplier_portal/dashboard.html', context)

@login_required
@user_passes_test(is_supplier)
def supplier_credit_history(request):
    """View all credit transactions for the supplier"""
    try:
        supplier = request.user.profile.supplier_link.supplier
    except AttributeError:
        messages.error(request, "Your profile is not linked to any supplier.")
        return redirect('dashboard')
        
    history = SupplierCreditTransaction.objects.filter(supplier=supplier).order_by('-created_at')
    
    return render(request, 'main/supplier_portal/credit_history.html', {
        'supplier': supplier,
        'history': history,
        'title': 'Credit History'
    })

@login_required
@user_passes_test(is_supplier)
def supplier_confirm_payment(request, transaction_id):
    """Supplier confirms they received a payment or adds notes"""
    try:
        supplier = request.user.profile.supplier_link.supplier
    except AttributeError:
        messages.error(request, "Your profile is not linked to any supplier.")
        return redirect('dashboard')
        
    trans = get_object_or_404(SupplierCreditTransaction, id=transaction_id, supplier=supplier, transaction_type='payment')
    
    if request.method == 'POST':
        supplier_notes = request.POST.get('supplier_notes')
        confirm = request.POST.get('confirm') == 'on'
        
        if confirm:
            trans.notes = f"{trans.notes or ''}\n[Supplier Confirmed: {datetime.date.today()}]"
            if supplier_notes:
                trans.notes += f"\nSupplier Note: {supplier_notes}"
            trans.save()
            messages.success(request, "Payment confirmed!")
        elif supplier_notes:
            trans.notes = f"{trans.notes or ''}\n[Supplier Note: {datetime.date.today()}]: {supplier_notes}"
            trans.save()
            messages.success(request, "Note added to payment.")
            
    return redirect('supplier_credit_history')

@login_required
@user_passes_test(is_supplier)
def supplier_po_list(request):
    """List of all POs for the supplier"""
    try:
        supplier = request.user.profile.supplier_link.supplier
    except AttributeError:
        messages.error(request, "Your profile is not linked to any supplier.")
        return redirect('dashboard')
        
    pos = PurchaseOrder.objects.filter(supplier=supplier).order_by('-created_at')
    
    return render(request, 'main/supplier_portal/po_list.html', {'pos': pos})

@login_required
@user_passes_test(is_supplier)
def supplier_po_detail(request, po_id):
    """Detailed view of a specific PO"""
    try:
        supplier = request.user.profile.supplier_link.supplier
    except AttributeError:
        messages.error(request, "Your profile is not linked to any supplier.")
        return redirect('dashboard')
        
    po = get_object_or_404(PurchaseOrder, id=po_id, supplier=supplier)
    
    return render(request, 'main/supplier_portal/po_detail.html', {'po': po})

@login_required
@user_passes_test(is_supplier)
def supplier_po_accept(request, po_id):
    """Supplier accepts the order"""
    try:
        supplier = request.user.profile.supplier_link.supplier
    except AttributeError:
        messages.error(request, "Your profile is not linked to any supplier.")
        return redirect('dashboard')
        
    po = get_object_or_404(PurchaseOrder, id=po_id, supplier=supplier, status='ordered')
    
    if request.method == 'POST':
        po.status = 'ordered' # Keep as ordered but maybe add a 'confirmed' status or note
        po.notes = f"{po.notes or ''}\n[Supplier Confirmed on {datetime.date.today()}]"
        po.save()
        
        # Log action
        from accounts.services.audit_service import AuditService
        AuditService.log_action(
            request, 
            'update', 
            f"Supplier {supplier.name} confirmed PO {po.reference_id}",
            target_model='PurchaseOrder',
            target_object_id=po.id
        )
        
        messages.success(request, f"Order {po.reference_id} confirmed!")
        return redirect('supplier_po_detail', po_id=po.id)

