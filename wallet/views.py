from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from main.models import Customer, Order, LoyaltyTransaction, GiftCard
from .forms import WalletLoginForm
from django.db.models import Sum

def wallet_login(request):
    """Simple phone-based login for customers"""
    if 'customer_id' in request.session:
        return redirect('wallet_dashboard')
        
    if request.method == 'POST':
        form = WalletLoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            try:
                customer = Customer.objects.get(phone=phone)
                request.session['customer_id'] = str(customer.id)
                messages.success(request, f"Welcome back, {customer.name}!")
                return redirect('wallet_dashboard')
            except Customer.DoesNotExist:
                messages.error(request, "Customer not found with this phone number.")
    else:
        form = WalletLoginForm()
            
    return render(request, 'wallet/login.html', {'form': form})

def wallet_dashboard(request):
    """Customer loyalty dashboard"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('wallet_login')
        
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Recent purchases
    recent_orders = Order.objects.filter(customer=customer).order_by('-created_at')[:5]
    
    # Gift cards
    gift_cards = GiftCard.objects.filter(customer=customer, status='active')
    
    # Loyalty history
    loyalty_history = LoyaltyTransaction.objects.filter(customer=customer).order_by('-created_at')[:10]
    
    context = {
        'customer': customer,
        'recent_orders': recent_orders,
        'gift_cards': gift_cards,
        'loyalty_history': loyalty_history,
        'title': 'MyWallet'
    }
    return render(request, 'wallet/dashboard.html', context)

def wallet_logout(request):
    """Log out from wallet session"""
    if 'customer_id' in request.session:
        del request.session['customer_id']
    return redirect('wallet_login')

from django.http import JsonResponse, HttpResponse

def manifest_json(request):
    """Serve PWA manifest"""
    tenant_name = request.user.profile.tenant.name if request.user.is_authenticated else "MyWallet"
    manifest = {
        "name": f"{tenant_name} MyWallet",
        "short_name": "MyWallet",
        "start_url": "/wallet/login/",
        "display": "standalone",
        "background_color": "#0f172a",
        "theme_color": "#4f46e5",
        "icons": [
            {
                "src": "/static/images/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/static/images/icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    return JsonResponse(manifest)

def service_worker_wallet(request):
    """Serve Wallet Service Worker"""
    sw_content = """
    const CACHE_NAME = 'wallet-v1';
    const ASSETS = [
        '/wallet/login/',
        '/wallet/dashboard/',
        'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap',
        'https://fonts.googleapis.com/icon?family=Material+Icons+Round'
    ];

    self.addEventListener('install', event => {
        event.waitUntil(
            caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
        );
    });

    self.addEventListener('fetch', event => {
        event.respondWith(
            caches.match(event.request).then(response => response || fetch(event.request))
        );
    });
    """
    return HttpResponse(sw_content, content_type="application/javascript")
