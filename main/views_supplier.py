from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
import random
import string
from .models import Supplier, SupplierProfile, SupplierCreditTransaction
from .forms import SupplierForm
from .forms_credit import SupplierPaymentForm
from branches.services.purchase_orders import PurchaseOrderService
from accounts.models import UserProfile

@login_required
def supplier_list(request):
    profile = request.user.profile
    tenant = profile.tenant
    
    # Permission check
    if profile.role not in ['admin', 'manager', 'financial']:
        return redirect('dashboard')
        
    query = request.GET.get('q', '')
    suppliers = Supplier.objects.filter(tenant=tenant)
    
    if query:
        suppliers = suppliers.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(tax_id__icontains=query) |
            Q(contact_person__icontains=query)
        )
    
    context = {
        'suppliers': suppliers,
        'query': query,
        'title': 'Suppliers'
    }
    return render(request, 'main/suppliers/list.html', context)

@login_required
def supplier_create(request):
    profile = request.user.profile
    tenant = profile.tenant
    
    if profile.role not in ['admin', 'manager']:
        return redirect('supplier_list')
        
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.tenant = tenant
            supplier.save()
            messages.success(request, f"Supplier '{supplier.name}' created successfully.")
            return redirect('supplier_list')
    else:
        form = SupplierForm()
        
    return render(request, 'main/suppliers/form.html', {'form': form, 'title': 'Add Supplier'})

@login_required
def supplier_update(request, supplier_id):
    profile = request.user.profile
    tenant = profile.tenant
    
    supplier = get_object_or_404(Supplier, id=supplier_id, tenant=tenant)
    
    if profile.role not in ['admin', 'manager']:
        return redirect('supplier_list')
        
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f"Supplier '{supplier.name}' updated successfully.")
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
        
    return render(request, 'main/suppliers/form.html', {'form': form, 'supplier': supplier, 'title': f'Edit {supplier.name}'})

@login_required
def supplier_delete(request, supplier_id):
    profile = request.user.profile
    tenant = profile.tenant
    
    if profile.role != 'admin':
        messages.error(request, "Only admins can delete suppliers.")
        return redirect('supplier_list')
        
    supplier = get_object_or_404(Supplier, id=supplier_id, tenant=tenant)
    name = supplier.name
    supplier.delete()
    
    messages.success(request, f"Supplier '{name}' deleted.")
    return redirect('supplier_list')

@login_required
def supplier_share_access(request, supplier_id):
    profile = request.user.profile
    tenant = profile.tenant
    
    if profile.role not in ['admin', 'manager']:
        messages.error(request, "Insufficient permissions.")
        return redirect('supplier_list')
        
    supplier = get_object_or_404(Supplier, id=supplier_id, tenant=tenant)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
            return redirect('supplier_list')
            
        try:
            with transaction.atomic():
                # Generate a random password
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                
                # 1. Create User
                user = User.objects.create_user(username=username, email=email, password=password)
                
                # 2. Create UserProfile
                user_profile = UserProfile.objects.create(
                    user=user,
                    tenant=tenant,
                    role='supplier'
                )
                
                # 3. Create SupplierProfile (The link)
                SupplierProfile.objects.create(
                    user_profile=user_profile,
                    supplier=supplier
                )
                
                messages.success(request, f"Access created for {supplier.name}! Share these credentials with them:\nUsername: {username}\nPassword: {password}")
                
        except Exception as e:
            messages.error(request, f"Error creating access: {str(e)}")
            
    return redirect('supplier_list')

@login_required
def supplier_detail(request, supplier_id):
    profile = request.user.profile
    tenant = profile.tenant
    
    if profile.role not in ['admin', 'manager', 'financial']:
        return redirect('supplier_list')
        
    supplier = get_object_or_404(Supplier, id=supplier_id, tenant=tenant)
    
    # Get credit history
    credit_history = SupplierCreditTransaction.objects.filter(supplier=supplier).order_by('-created_at')[:50]
    
    # Payment Form
    payment_form = SupplierPaymentForm()
    
    context = {
        'supplier': supplier,
        'credit_history': credit_history,
        'payment_form': payment_form,
        'title': supplier.name
    }
    return render(request, 'main/suppliers/detail.html', context)

@login_required
def record_supplier_payment(request, supplier_id):
    profile = request.user.profile
    tenant = profile.tenant
    
    if profile.role not in ['admin', 'manager', 'financial']:
        return redirect('supplier_list')
        
    supplier = get_object_or_404(Supplier, id=supplier_id, tenant=tenant)
    
    if request.method == 'POST':
        form = SupplierPaymentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                service = PurchaseOrderService(tenant=tenant, user_profile=profile)
                service.record_supplier_payment(
                    supplier=supplier,
                    amount=form.cleaned_data['amount'],
                    user_profile=profile,
                    notes=form.cleaned_data['notes'],
                    receipt_image=form.cleaned_data['receipt_image']
                )
                messages.success(request, f"Payment of {form.cleaned_data['amount']} recorded for {supplier.name}.")
            except Exception as e:
                messages.error(request, f"Error recording payment: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
            
    return redirect('supplier_detail', supplier_id=supplier.id)

