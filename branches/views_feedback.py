from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Branch, Tenant
from main.models import CustomerFeedback, Order
from .forms_feedback import CustomerFeedbackForm

# Admin Views
@login_required
def feedback_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    # Permission check
    if request.user.profile.role not in ['admin', 'manager']:
        return redirect('branch_dashboard', branch_id=branch.id)
        
    # Feedback is tenant-wide usually, but we can filter by branch transactions if needed
    # For now, let's show all feedback for the tenant associated with customers who might shop at this branch
    feedback = CustomerFeedback.objects.filter(tenant=request.user.profile.tenant).order_by('-created_at')
    
    context = {
        'branch': branch,
        'feedback_list': feedback,
        'title': 'Customer Feedback'
    }
    return render(request, 'branches/crm/feedback_list.html', context)

# Public Views (No Login Required)
def public_feedback_submit(request, tenant_id, order_uuid=None):
    """
    Public feedback form. 
    order_uuid is optional data passed to pre-fill or link transaction.
    """
    tenant = get_object_or_404(Tenant, pk=tenant_id)
    order = None
    if order_uuid:
        # Assuming we have a UUID or similar token in Order model (we added offline_uuid, let's use ID for now or check model)
        # Checking model... Order has offline_uuid but mostly internal. Let's assume ID for simplicity or offline_uuid if robust.
        # For security, verifying by ID alone is risky if sequential. 
        # For this MVP, we will rely on a generic form or simple ID lookup if provided.
        pass

    if request.method == 'POST':
        form = CustomerFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.tenant = tenant
            # If we had order logic: feedback.transaction = order
            # feedback.customer = ... (Public form needs to identify customer or create anonymous?)
            # The model requires 'customer'. This implies we need to identify them.
            # Fix: We'll ask for Email/Phone in the form and look them up or create a dummy "Guest" customer.
            
            # Simple Lookup Strategy
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            
            from main.models import Customer
            customer = Customer.objects.filter(tenant=tenant, email=email).first()
            if not customer and phone:
                 customer = Customer.objects.filter(tenant=tenant, phone=phone).first()
            
            if not customer:
                # Create Guest Customer
                customer = Customer.objects.create(
                    tenant=tenant,
                    name=form.cleaned_data.get('name', 'Guest'),
                    email=email,
                    phone=phone,
                    customer_type='retail'
                )
            
            feedback.customer = customer
            feedback.save()
            
            return render(request, 'main/feedback_success.html', {'tenant': tenant})
    else:
        form = CustomerFeedbackForm()
        
    context = {
        'tenant': tenant,
        'form': form,
    }
    return render(request, 'main/feedback_form.html', context)
