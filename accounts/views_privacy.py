import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from main.models import Customer
from .utils import log_activity
from .models import UserProfile
import uuid

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'admin'

from accounts.utils import merchant_only

@login_required
@merchant_only
@user_passes_test(is_admin)
def privacy_dashboard(request):
    """Overview of privacy tools"""
    customers = Customer.objects.filter(branch__tenant=request.user.profile.tenant)
    context = {'customers': customers[:10], 'total_customers': customers.count()}
    return render(request, 'accounts/privacy/dashboard.html', context)

@login_required
@merchant_only
@user_passes_test(is_admin)
def export_customer_data(request, customer_id):
    """Export all data related to a customer as JSON"""
    customer = get_object_or_404(Customer, pk=customer_id, branch__tenant=request.user.profile.tenant)
    
    # Gather data
    data = {
        'profile': {
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'address': customer.address,
            'created_at': str(customer.created_at),
        },
        'orders': [],
        'loyalty': {
             'points': float(customer.loyalty_points)
        }
    }
    
    for order in customer.orders.all():
        data['orders'].append({
            'id': order.id,
            'date': str(order.created_at),
            'total': float(order.total_amount),
            'items': [{'product': item.product.name if item.product else 'Unknown', 'qty': item.quantity, 'price': float(item.price)} for item in order.items.all()]
        })
        
    response = HttpResponse(
        json.dumps(data, indent=4),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="customer_data_{customer.id}.json"'
    
    log_activity(request, 'export', f"Exported data for customer {customer.name}", 'Customer', customer.id)
    
    return response

@login_required
@merchant_only
@user_passes_test(is_admin)
def anonymize_customer(request, customer_id):
    """GDPR Right to be Forgotten - Anonymize PII"""
    customer = get_object_or_404(Customer, pk=customer_id, branch__tenant=request.user.profile.tenant)
    
    if request.method == 'POST':
        original_name = customer.name
        
        # Anonymize
        uid = str(uuid.uuid4())[:8]
        customer.name = f"Anonymized User {uid}"
        customer.email = f"deleted_{uid}@example.com"
        customer.phone = ""
        customer.address = "Redacted"
        customer.save()
        
        log_activity(request, 'update', f"Anonymized customer {original_name} (GDPR)", 'Customer', customer.id)
        
        messages.success(request, f"Customer {original_name} has been anonymized.")
        return redirect('privacy_dashboard')
        
    return render(request, 'accounts/privacy/confirm_anonymize.html', {'customer': customer})
