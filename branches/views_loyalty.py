from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Branch
from main.models import CRMSettings, CustomerTier
from .forms_loyalty import CRMSettingsForm, CustomerTierForm

@login_required
def loyalty_dashboard(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    # Only Admin or Manager
    if request.user.profile.role not in ['admin', 'manager']:
        return redirect('branch_dashboard', branch_id=branch.id)
        
    settings, created = CRMSettings.objects.get_or_create(tenant=request.user.profile.tenant)
    tiers = CustomerTier.objects.filter(tenant=request.user.profile.tenant).order_by('min_spend')
    
    if request.method == 'POST':
        form = CRMSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loyalty settings updated successfully.')
            return redirect('loyalty_dashboard', branch_id=branch.id)
    else:
        form = CRMSettingsForm(instance=settings)
        
    context = {
        'branch': branch,
        'settings': settings,
        'tiers': tiers,
        'form': form,
        'title': 'Loyalty Program'
    }
    return render(request, 'branches/crm/loyalty_dashboard.html', context)

@login_required
def tier_create(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    if request.method == 'POST':
        form = CustomerTierForm(request.POST)
        if form.is_valid():
            tier = form.save(commit=False)
            tier.tenant = request.user.profile.tenant
            tier.save()
            messages.success(request, f'Tier "{tier.name}" created successfully.')
            return redirect('loyalty_dashboard', branch_id=branch.id)
    else:
        form = CustomerTierForm()
        
    context = {
        'branch': branch,
        'form': form,
        'title': 'Add Tier'
    }
    return render(request, 'branches/crm/tier_form.html', context)

@login_required
def tier_update(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    tier = get_object_or_404(CustomerTier, pk=pk, tenant=request.user.profile.tenant)
    
    if request.method == 'POST':
        form = CustomerTierForm(request.POST, instance=tier)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tier "{tier.name}" updated successfully.')
            return redirect('loyalty_dashboard', branch_id=branch.id)
    else:
        form = CustomerTierForm(instance=tier)
        
    context = {
        'branch': branch,
        'form': form,
        'title': 'Edit Tier'
    }
    return render(request, 'branches/crm/tier_form.html', context)

@login_required
def tier_delete(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    tier = get_object_or_404(CustomerTier, pk=pk, tenant=request.user.profile.tenant)
    
    if request.method == 'POST':
        tier.delete()
        messages.success(request, 'Tier deleted successfully.')
        return redirect('loyalty_dashboard', branch_id=branch.id)
    
    context = {
        'branch': branch,
        'tier': tier,
        'title': 'Delete Tier'
    }
    return render(request, 'branches/crm/tier_confirm_delete.html', context)
