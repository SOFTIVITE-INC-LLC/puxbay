from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from branches.models_workforce import CommissionRule
from .forms import CommissionRuleForm
from accounts.models import Branch

@login_required
def commission_rule_list(request):
    """Global list of commission rules for the tenant"""
    tenant = request.user.profile.tenant
    rules = CommissionRule.objects.filter(tenant=tenant).order_by('min_sales_amount')
    
    return render(request, 'main/workforce/commission_rule_list.html', {
        'rules': rules
    })

@login_required
def commission_rule_create(request):
    """Create a new commission rule"""
    tenant = request.user.profile.tenant
    
    if request.method == 'POST':
        form = CommissionRuleForm(request.POST)
        if form.is_valid():
            rule = form.save(commit=False)
            rule.tenant = tenant
            rule.save()
            messages.success(request, "Commission rule created successfully!")
            return redirect('commission_rule_list')
    else:
        form = CommissionRuleForm()
        # Filter branches to tenant's branches only
        form.fields['branch'].queryset = Branch.objects.filter(tenant=tenant)
        
    return render(request, 'main/workforce/commission_rule_form.html', {
        'form': form,
        'title': 'Create Commission Rule'
    })

@login_required
def commission_rule_delete(request, pk):
    """Delete a commission rule"""
    rule = get_object_or_404(CommissionRule, pk=pk, tenant=request.user.profile.tenant)
    rule.delete()
    messages.success(request, "Commission rule deleted.")
    return redirect('commission_rule_list')
