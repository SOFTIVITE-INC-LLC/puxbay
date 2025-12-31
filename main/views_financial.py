"""
Financial Management Views
Handles expense tracking, P&L reports, tax reports, payment gateways, and returns
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F, DecimalField
from django.db.models.functions import TruncDate, Coalesce
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
from decimal import Decimal
import csv

from .models import (
    ExpenseCategory, Expense, TaxConfiguration, PaymentMethod, 
    Payment, Return, ReturnItem, Order, OrderItem, Product, Customer
)
from .forms_financial import (
    ExpenseCategoryForm, ExpenseForm, TaxConfigurationForm,
    PaymentMethodForm, ReturnForm, ReturnItemFormSet
)
from accounts.models import Branch
from .payment_processors import get_payment_processor

# =============================================================================
# EXPENSE MANAGEMENT
# =============================================================================

@login_required
def expense_category_list(request):
    """List all expense categories"""
    tenant = request.user.profile.tenant
    categories = ExpenseCategory.objects.filter(tenant=tenant).annotate(
        expense_count=Count('expenses'),
        total_amount=Coalesce(Sum('expenses__amount'), Decimal('0.00'))
    )
    
    context = {
        'categories': categories,
    }
    return render(request, 'main/expense_category_list.html', context)

@login_required
def expense_category_create(request):
    """Create a new expense category"""
    tenant = request.user.profile.tenant
    
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.tenant = tenant
            category.save()
            messages.success(request, f'Expense category "{category.name}" created successfully!')
            return redirect('expense_category_list')
    else:
        form = ExpenseCategoryForm()
    
    context = {'form': form}
    return render(request, 'main/expense_category_form.html', context)

@login_required
def expense_category_update(request, pk):
    """Update an expense category"""
    tenant = request.user.profile.tenant
    category = get_object_or_404(ExpenseCategory, pk=pk, tenant=tenant)
    
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Expense category "{category.name}" updated successfully!')
            return redirect('expense_category_list')
    else:
        form = ExpenseCategoryForm(instance=category)
    
    context = {'form': form, 'category': category}
    return render(request, 'main/expense_category_form.html', context)

@login_required
def expense_category_delete(request, pk):
    """Delete an expense category"""
    tenant = request.user.profile.tenant
    category = get_object_or_404(ExpenseCategory, pk=pk, tenant=tenant)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Expense category "{category_name}" deleted successfully!')
        return redirect('expense_category_list')
    
    context = {'category': category}
    return render(request, 'main/expense_category_confirm_delete.html', context)

@login_required
def expense_list(request):
    """List all expenses with filtering"""
    tenant = request.user.profile.tenant
    
    # Get filter parameters
    category_id = request.GET.get('category')
    branch_id = request.GET.get('branch')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Base queryset
    expenses = Expense.objects.filter(tenant=tenant).select_related(
        'category', 'branch', 'created_by'
    )
    
    # Apply filters
    if category_id:
        expenses = expenses.filter(category_id=category_id)
    if branch_id:
        expenses = expenses.filter(branch_id=branch_id)
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
    categories = ExpenseCategory.objects.filter(tenant=tenant)
    branches = tenant.branches.all()
    
    context = {
        'expenses': expenses,
        'summary': summary,
        'category_breakdown': category_breakdown,
        'categories': categories,
        'branches': branches,
        'filters': {
            'category': category_id,
            'branch': branch_id,
            'start_date': start_date,
            'end_date': end_date,
        }
    }
    return render(request, 'main/expense_list.html', context)

@login_required
def expense_create(request):
    """Create a new expense"""
    tenant = request.user.profile.tenant
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, tenant=tenant)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.tenant = tenant
            expense.created_by = request.user.profile
            expense.save()
            messages.success(request, 'Expense recorded successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(tenant=tenant)
    
    context = {'form': form}
    return render(request, 'main/expense_form.html', context)

@login_required
def expense_update(request, pk):
    """Update an expense"""
    tenant = request.user.profile.tenant
    expense = get_object_or_404(Expense, pk=pk, tenant=tenant)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense, tenant=tenant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense, tenant=tenant)
    
    context = {'form': form, 'expense': expense}
    return render(request, 'main/expense_form.html', context)

@login_required
def expense_delete(request, pk):
    """Delete an expense"""
    tenant = request.user.profile.tenant
    expense = get_object_or_404(Expense, pk=pk, tenant=tenant)
    
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('expense_list')
    
    context = {'expense': expense}
    return render(request, 'main/expense_confirm_delete.html', context)

# =============================================================================
# PROFIT & LOSS REPORT
# =============================================================================

@login_required
def profit_loss_report(request):
    """Generate Profit & Loss statement"""
    tenant = request.user.profile.tenant
    
    # Date range filtering
    date_range = request.GET.get('range', 'month')
    today = timezone.now().date()
    
    if date_range == 'today':
        start_date = today
        end_date = today
    elif date_range == 'week':
        start_date = today - timedelta(days=7)
        end_date = today + timedelta(days=1)
    elif date_range == 'month':
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=1)
    elif date_range == 'year':
        start_date = today - timedelta(days=365)
        end_date = today + timedelta(days=1)
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
    
    # Revenue calculations
    orders_query = Order.objects.filter(tenant=tenant, status='completed')
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
        total_cogs=Coalesce(Sum(F('quantity') * F('cost_price'), output_field=DecimalField()), Decimal('0.00'))
    )['total_cogs']
    
    # Gross profit
    gross_revenue = revenue_data['total_revenue'] - revenue_data['total_tax']
    gross_profit = gross_revenue - cogs
    gross_margin = (gross_profit / gross_revenue * 100) if gross_revenue > 0 else 0
    
    # Expense calculations
    expenses_query = Expense.objects.filter(tenant=tenant)
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
    
    # Branch performance
    branch_performance = orders_query.values('branch__name').annotate(
        revenue=Sum('total_amount'),
        orders=Count('id')
    ).order_by('-revenue')
    
    context = {
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
        'branch_performance': branch_performance,
    }
    return render(request, 'main/profit_loss_report.html', context)

# =============================================================================
# TAX REPORTS
# =============================================================================

@login_required
def tax_configuration(request):
    """Configure tax settings"""
    tenant = request.user.profile.tenant
    
    try:
        tax_config = TaxConfiguration.objects.get(tenant=tenant)
    except TaxConfiguration.DoesNotExist:
        tax_config = None
    
    if request.method == 'POST':
        form = TaxConfigurationForm(request.POST, instance=tax_config)
        if form.is_valid():
            config = form.save(commit=False)
            config.tenant = tenant
            config.save()
            messages.success(request, 'Tax configuration updated successfully!')
            return redirect('tax_report')
    else:
        form = TaxConfigurationForm(instance=tax_config)
    
    context = {'form': form, 'tax_config': tax_config}
    return render(request, 'main/tax_configuration.html', context)

@login_required
def tax_report(request):
    """Generate tax report"""
    tenant = request.user.profile.tenant
    
    # Get tax configuration
    try:
        tax_config = TaxConfiguration.objects.get(tenant=tenant)
    except TaxConfiguration.DoesNotExist:
        messages.warning(request, 'Please configure tax settings first.')
        return redirect('tax_configuration')
    
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
    
    # Get completed orders
    orders_query = Order.objects.filter(tenant=tenant, status='completed')
    if start_date and end_date:
        orders_query = orders_query.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
    
    # Tax calculations
    tax_summary = orders_query.aggregate(
        total_sales=Coalesce(Sum('total_amount'), Decimal('0.00')),
        total_tax_collected=Coalesce(Sum('tax_amount'), Decimal('0.00')),
        taxable_amount=Coalesce(Sum('subtotal'), Decimal('0.00')),
        order_count=Count('id')
    )
    
    # Tax by branch
    tax_by_branch = orders_query.values('branch__name').annotate(
        sales=Sum('total_amount'),
        tax=Sum('tax_amount'),
        orders=Count('id')
    ).order_by('-tax')
    
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
        'tax_config': tax_config,
        'date_range': date_range,
        'start_date': start_date,
        'end_date': end_date,
        'tax_summary': tax_summary,
        'tax_by_branch': tax_by_branch,
        'daily_tax': daily_tax,
    }
    return render(request, 'main/tax_report.html', context)

@login_required
def tax_report_export(request):
    """Export tax report as CSV"""
    tenant = request.user.profile.tenant
    
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    orders_query = Order.objects.filter(tenant=tenant, status='completed')
    if start_date and end_date:
        orders_query = orders_query.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="tax_report_{timezone.now().date()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Date', 'Branch', 'Subtotal', 'Tax Amount', 'Total', 'Payment Method'])
    
    for order in orders_query:
        writer.writerow([
            order.id,
            order.created_at.strftime('%Y-%m-%d'),
            order.branch.name if order.branch else 'N/A',
            order.subtotal,
            order.tax_amount,
            order.total_amount,
            order.get_payment_method_display()
        ])
    
    return response

# =============================================================================
# PAYMENT GATEWAY MANAGEMENT
# =============================================================================

@login_required
def payment_settings(request):
    """Manage payment gateway settings"""
    tenant = request.user.profile.tenant
    payment_methods = PaymentMethod.objects.filter(tenant=tenant)
    
    context = {
        'payment_methods': payment_methods,
    }
    return render(request, 'main/payment_settings.html', context)

@login_required
def payment_method_create(request):
    """Create a new payment method"""
    tenant = request.user.profile.tenant
    
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            method = form.save(commit=False)
            method.tenant = tenant
            method.save()
            messages.success(request, f'Payment method "{method.name}" added successfully!')
            return redirect('payment_settings')
    else:
        form = PaymentMethodForm()
    
    context = {'form': form}
    return render(request, 'main/payment_method_form.html', context)

@login_required
def payment_method_update(request, pk):
    """Update a payment method"""
    tenant = request.user.profile.tenant
    method = get_object_or_404(PaymentMethod, pk=pk, tenant=tenant)
    
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=method)
        if form.is_valid():
            form.save()
            messages.success(request, f'Payment method "{method.name}" updated successfully!')
            return redirect('payment_settings')
    else:
        form = PaymentMethodForm(instance=method)
    
    context = {'form': form, 'method': method}
    return render(request, 'main/payment_method_form.html', context)

@login_required
def payment_method_delete(request, pk):
    """Delete a payment method"""
    tenant = request.user.profile.tenant
    method = get_object_or_404(PaymentMethod, pk=pk, tenant=tenant)
    
    if request.method == 'POST':
        method_name = method.name
        method.delete()
        messages.success(request, f'Payment method "{method_name}" deleted successfully!')
        return redirect('payment_settings')
    
    context = {'method': method}
    return render(request, 'main/payment_method_confirm_delete.html', context)

@login_required
def test_payment_connection(request, pk):
    """Test payment gateway connection"""
    tenant = request.user.profile.tenant
    method = get_object_or_404(PaymentMethod, pk=pk, tenant=tenant)
    
    processor = get_payment_processor(method.provider)
    
    if not processor:
        return JsonResponse({
            'status': 'error',
            'message': f'{method.provider} processor not configured or credentials missing'
        })
    
    # Test with a small amount (0.50)
    result = processor.process_payment(
        amount=Decimal('0.50'),
        currency='USD',
        metadata={'test': True, 'tenant': tenant.name}
    )
    
    return JsonResponse(result)

# =============================================================================
# RETURNS & REFUNDS MANAGEMENT
# =============================================================================

@login_required
def return_list(request, branch_id=None):
    """List all return requests"""
    tenant = request.user.profile.tenant
    branch = None
    if branch_id:
        branch = get_object_or_404(Branch, pk=branch_id, tenant=tenant)
    
    # Filter by status
    status_filter = request.GET.get('status', 'all')
    
    returns = Return.objects.filter(tenant=tenant).select_related(
        'branch', 'order', 'customer', 'created_by'
    ).prefetch_related('items')
    
    if branch:
        returns = returns.filter(branch=branch)
    
    if status_filter != 'all':
        returns = returns.filter(status=status_filter)
    
    # Summary statistics
    summary = {
        'pending': returns.filter(status='pending').count(),
        'approved': returns.filter(status='approved').count(),
        'completed': returns.filter(status='completed').count(),
        'rejected': returns.filter(status='rejected').count(),
        'total_refund_amount': returns.filter(
            status__in=['approved', 'completed']
        ).aggregate(total=Coalesce(Sum('refund_amount'), Decimal('0.00')))['total']
    }
    
    context = {
        'returns': returns,
        'summary': summary,
        'status_filter': status_filter,
        'branch': branch,
    }
    return render(request, 'main/return_list.html', context)

@login_required
def return_create(request, branch_id):
    """Create a new return request"""
    tenant = request.user.profile.tenant
    branch = get_object_or_404(Branch, pk=branch_id, tenant=tenant)
    
    order_id = request.GET.get('order_id')
    initial_data = {}
    if order_id:
        initial_data['order'] = order_id
        order = Order.objects.filter(id=order_id, tenant=tenant, branch=branch).first()
        if order:
            initial_data['customer'] = order.customer_id
    
    if request.method == 'POST':
        form = ReturnForm(request.POST, tenant=tenant, branch=branch)
        
        # Get selected order from POST to filter formset items
        post_order_id = request.POST.get('order')
        post_order = Order.objects.filter(id=post_order_id, tenant=tenant, branch=branch).first() if post_order_id else None
        formset = ReturnItemFormSet(request.POST, prefix='items', order=post_order)
        
        if form.is_valid() and formset.is_valid():
            return_request = form.save(commit=False)
            return_request.tenant = tenant
            return_request.branch = branch
            return_request.created_by = request.user.profile
            return_request.save()
            
            # Save return items
            formset.instance = return_request
            items = formset.save(commit=False)
            
            # Calculate refund amount and set unit prices
            total_refund = Decimal('0.00')
            for item in items:
                # Get the original order item to set the unit price
                order_item = OrderItem.objects.filter(
                    order=return_request.order,
                    product=item.product
                ).first()
                
                if order_item:
                    item.unit_price = order_item.price
                    total_refund += item.get_total_value()
                item.save()
            
            # Update return request refund amount
            return_request.refund_amount = total_refund
            return_request.save()
            
            messages.success(request, 'Return request created successfully!')
            return redirect('branch_return_detail', branch_id=return_request.branch.id, pk=return_request.pk)
    else:
        # Get order from GET param if available for initial filtering
        get_order = Order.objects.filter(id=order_id, tenant=tenant, branch=branch).first() if order_id else None
        form = ReturnForm(tenant=tenant, branch=branch, initial=initial_data)
        formset = ReturnItemFormSet(prefix='items', order=get_order)
    
    context = {
        'form': form,
        'formset': formset,
        'branch': branch,
    }
    return render(request, 'main/return_form.html', context)

@login_required
def return_detail(request, pk, branch_id=None):
    """View return request details"""
    tenant = request.user.profile.tenant
    branch = None
    if branch_id:
        branch = get_object_or_404(Branch, pk=branch_id, tenant=tenant)
        
    return_request = get_object_or_404(
        Return.objects.prefetch_related('items__product'),
        pk=pk,
        tenant=tenant
    )
    
    # If branch_id was provided, ensure it matches return_request.branch
    if branch and return_request.branch != branch:
        messages.error(request, "This return belongs to another branch.")
        return redirect('return_list')

    context = {
        'return_request': return_request,
        'net_refund': return_request.get_net_refund(),
        'branch': branch or return_request.branch,
    }
    return render(request, 'main/return_detail.html', context)

@login_required
def return_approve(request, pk):
    """Approve a return request"""
    if request.user.profile.role not in ['admin', 'manager', 'financial']:
        messages.error(request, "Access Denied: Only managers, admins, or financial staff can approve returns.")
        return redirect('return_detail', pk=pk)
        
    tenant = request.user.profile.tenant
    return_request = get_object_or_404(Return, pk=pk, tenant=tenant, status='pending')
    
    if request.method == 'POST':
        return_request.status = 'approved'
        return_request.approved_by = request.user.profile
        return_request.approved_at = timezone.now()
        return_request.save()
        
        messages.success(request, f'Return request #{return_request.id} approved!')
        return redirect('branch_return_detail', branch_id=return_request.branch.id, pk=pk)
    
    return redirect('branch_return_detail', branch_id=return_request.branch.id, pk=pk)

@login_required
def return_reject(request, pk):
    """Reject a return request"""
    if request.user.profile.role not in ['admin', 'manager', 'financial']:
        messages.error(request, "Access Denied: Only managers, admins, or financial staff can reject returns.")
        return redirect('return_detail', pk=pk)
        
    tenant = request.user.profile.tenant
    return_request = get_object_or_404(Return, pk=pk, tenant=tenant, status='pending')
    
    if request.method == 'POST':
        return_request.status = 'rejected'
        return_request.approved_by = request.user.profile
        return_request.approved_at = timezone.now()
        return_request.save()
        
        messages.warning(request, f'Return request #{return_request.id} rejected!')
        return redirect('branch_return_detail', branch_id=return_request.branch.id, pk=pk)
    
    return redirect('branch_return_detail', branch_id=return_request.branch.id, pk=pk)

@login_required
def return_process_refund(request, pk):
    """Process refund for an approved return"""
    if request.user.profile.role not in ['admin', 'manager', 'financial']:
        messages.error(request, "Access Denied: Only managers, admins, or financial staff can process refunds.")
        return redirect('return_detail', pk=pk)
        
    tenant = request.user.profile.tenant
    return_request = get_object_or_404(Return, pk=pk, tenant=tenant, status='approved')
    
    if request.method == 'POST':
        # Restock items if needed
        for item in return_request.items.filter(restock=True):
            if item.product:
                item.product.stock_quantity += item.quantity
                item.product.save()
        
        # Process refund based on method
        if return_request.refund_method in ['cash', 'store_credit']:
            # Direct refund - mark as completed
            return_request.status = 'completed'
            return_request.completed_at = timezone.now()
            return_request.save()
            
            # If store credit, add to customer balance
            if return_request.refund_method == 'store_credit' and return_request.customer:
                return_request.customer.store_credit_balance += return_request.get_net_refund()
                return_request.customer.save()
                
                # Create transaction record for audit
                StoreCreditTransaction.objects.create(
                    tenant=tenant,
                    customer=return_request.customer,
                    amount=return_request.get_net_refund(),
                    reference=f"Refund for Return #{return_request.id}"
                )
            
            messages.success(request, f'Refund of ${return_request.get_net_refund()} processed successfully!')
        
        elif return_request.refund_method in ['card', 'original']:
            # Process through payment gateway
            original_payment = Payment.objects.filter(order=return_request.order).first()
            
            if original_payment and original_payment.payment_method.provider in ['stripe', 'paypal']:
                processor = get_payment_processor(original_payment.payment_method.provider)
                
                if processor:
                    result = processor.process_refund(
                        transaction_id=original_payment.transaction_id,
                        amount=return_request.get_net_refund()
                    )
                    
                    if result['status'] == 'success':
                        return_request.status = 'completed'
                        return_request.completed_at = timezone.now()
                        return_request.save()
                        
                        # Create refund payment record
                        Payment.objects.create(
                            tenant=tenant,
                            order=return_request.order,
                            payment_method=original_payment.payment_method,
                            amount=-return_request.get_net_refund(),  # Negative for refund
                            status='refunded',
                            transaction_id=result.get('refund_id'),
                            metadata=result.get('metadata')
                        )
                        
                        messages.success(request, f'Refund of ${return_request.get_net_refund()} processed through {original_payment.payment_method.provider}!')
                    else:
                        messages.error(request, f'Refund failed: {result.get("error")}')
                else:
                    messages.error(request, 'Payment processor not available')
            else:
                messages.error(request, 'Original payment method not found or not supported')
        
        return redirect('branch_return_detail', branch_id=return_request.branch.id, pk=pk)
    
    return redirect('branch_return_detail', branch_id=return_request.branch.id, pk=pk)
