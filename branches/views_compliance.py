from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import CashDrawerSession, Branch
from .forms import CashSessionForm, CashDrawerCloseForm
from main.models import Order
from django.db.models import Sum, DecimalField
from decimal import Decimal

@login_required
def open_drawer(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    # Check if already open
    active_session = CashDrawerSession.objects.filter(
        branch=branch, 
        end_time__isnull=True, 
        status='open'
    ).first()
    
    if active_session:
        messages.warning(request, "A drawer session is already open.")
        return redirect('branch_dashboard', branch_id=branch.id)
    
    if request.method == 'POST':
        form = CashSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.tenant = branch.tenant
            session.branch = branch
            session.employee = request.user.profile
            session.status = 'open'
            session.save()
            
            messages.success(request, "Cash drawer opened successfully.")
            return redirect('branch_dashboard', branch_id=branch.id)
    else:
        form = CashSessionForm()
        
    return render(request, 'branches/compliance/open_drawer.html', {
        'branch': branch,
        'form': form,
    })

@login_required
def close_drawer(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    session = CashDrawerSession.objects.filter(
        branch=branch, 
        end_time__isnull=True, 
        status='open'
    ).first()
    
    if not session:
        messages.error(request, "No open session found to close.")
        return redirect('open_drawer', branch_id=branch.id)
        
    # Calculate Expected Cash (Starting + Cash Sales)
    # Filter orders completed during this session
    session_sales = Order.objects.filter(
        branch=branch,
        created_at__gte=session.start_time,
        payment_method='cash',  # Assuming 'cash' is the stored value
        status='completed'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    session.expected_cash = session.starting_balance + session_sales
    
    if request.method == 'POST':
        form = CashDrawerCloseForm(request.POST, instance=session)
        if form.is_valid():
            session = form.save(commit=False)
            session.difference = session.actual_cash - session.expected_cash
            session.end_time = timezone.now()
            session.status = 'closed'
            if form.cleaned_data.get('notes'):
                session.notes += f"\nClosed by {request.user.username}. Notes: {form.cleaned_data['notes']}"
            session.save()
            
            messages.success(request, f"Drawer closed. Discrepancy: ${session.difference}")
            return redirect('eod_report', branch_id=branch.id, session_id=session.id)
    else:
        form = CashDrawerCloseForm(instance=session)
        
    context = {
        'branch': branch,
        'session': session,
        'sales_total': session_sales,
        'form': form,
    }
    return render(request, 'branches/compliance/close_drawer.html', context)

@login_required
def eod_report(request, branch_id, session_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    session = get_object_or_404(CashDrawerSession, pk=session_id, branch=branch)
    
    context = {
        'branch': branch,
        'session': session,
    }
    return render(request, 'branches/compliance/eod_report.html', context)
