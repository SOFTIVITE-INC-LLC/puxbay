from django.shortcuts import render, get_object_or_404
from .models import Customer, Order
from accounts.models import Tenant

def customer_portal_login(request):
    """Entry point for the customer portal"""
    if request.method == 'POST':
        phone = request.POST.get('phone')
        # In a real app, we'd use a 6-digit OTP or similar secure auth.
        # For this requirement, we'll fetch by phone.
        customer = Customer.objects.filter(phone=phone).first()
        
        if customer:
            # Simple session-less (or session-based) view
            recent_orders = Order.objects.filter(customer=customer, status='completed').order_by('-created_at')[:10]
            return render(request, 'main/customer_portal_dashboard.html', {
                'customer': customer,
                'recent_orders': recent_orders,
                'tenant': customer.tenant
            })
        else:
            return render(request, 'main/customer_portal_login.html', {
                'error': 'Customer not found with this phone number.'
            })
            
    return render(request, 'main/customer_portal_login.html')

def public_customer_portal(request, tenant_id):
    """Direct link for a merchant to share with their customers"""
    tenant = get_object_or_404(Tenant, id=tenant_id)
    return render(request, 'main/customer_portal_login.html', {
        'tenant': tenant
    })
