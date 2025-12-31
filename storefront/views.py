from django.http import JsonResponse
from django.db.models import Avg, Count
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.models import Tenant, Branch
from main.models import Product, Order, OrderItem, Customer, Category, ProductVariant, CRMSettings, LoyaltyTransaction
# from django.contrib.postgres.search import TrigramSimilarity
from django.db import transaction
from django.db.models import Q
from django.conf import settings as django_settings
import stripe

from .models import StorefrontSettings, ProductReview, Wishlist, Coupon, NewsletterSubscription, ProductImageGallery, AbandonedCart
from .forms import (
    StorefrontSettingsForm, CustomerRegistrationForm, CustomerLoginForm,
    CheckoutForm, ProductReviewForm, NewsletterSubscriptionForm, ContactForm,
    CustomerProfileForm, CouponApplyForm, TrackOrderForm
)
from .decorators import storefront_active_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User

# Configure Stripe Default (Fallback)
stripe.api_key = getattr(django_settings, 'STRIPE_SECRET_KEY', '')

def save_abandoned_cart(request, tenant, email=None):
    cart = request.session.get('cart', {})
    if not cart:
        # If cart is empty, we might want to delete an existing abandoned cart? 
        # Usually we just leave it or don't create it.
        return None
    
    if not email and request.user.is_authenticated:
        email = request.user.email
    
    if not email:
        return None
    
    abandoned_cart, created = AbandonedCart.objects.get_or_create(
        tenant=tenant,
        email=email,
        is_recovered=False,
        defaults={'cart_data': cart}
    )
    if not created:
        abandoned_cart.cart_data = cart
        abandoned_cart.save()
    
    return abandoned_cart

def get_context(request, tenant_slug, branch_id):
    tenant = get_object_or_404(Tenant, subdomain=tenant_slug)
    branch = get_object_or_404(Branch, id=branch_id, tenant=tenant)
    
    # Try to get settings for this tenant. 
    # filter by tenant to ensure we get the correct settings
    store_settings = StorefrontSettings.objects.filter(tenant=tenant).first()
    
    # Auto-create if missing for smoother UX
    if not store_settings:
        store_settings = StorefrontSettings.objects.create(
            tenant=tenant, 
            default_branch=branch, 
            is_active=False, 
            store_name=tenant.name
        )
    elif not store_settings.tenant:
        # Maintenance: Ensure tenant is linked if it somehow got lost
        store_settings.tenant = tenant
        store_settings.save()
        
    # --- Cart Context ---
    cart = request.session.get('cart', {})
    cart_preview = []
    if cart:
        # Efficiently fetch products
        products = Product.objects.filter(id__in=cart.keys())
        product_map = {str(p.id): p for p in products}
        
        for pid, qty in cart.items():
            product = product_map.get(str(pid))
            if product:
                cart_preview.append({
                    'product': product,
                    'quantity': qty
                })
    
    # --- Customer Context ---
    customer = None
    if request.user.is_authenticated:
        customer = Customer.objects.filter(user=request.user, tenant=tenant).first()

    # --- Categories Context ---
    categories = Category.objects.filter(tenant=tenant, branch=branch)

    # --- Abandoned Cart Sync ---
    if request.user.is_authenticated:
        save_abandoned_cart(request, tenant)

    return tenant, branch, store_settings, cart_preview, customer, categories


@storefront_active_required
def store_home(request, tenant_slug, branch_id):
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)

    # Base queryset
    products = Product.objects.filter(tenant=tenant, branch=branch, is_active=True)
    
    # categories is already fetched in get_context, but we might want annotated counts specifically for home page
    from django.db.models import Count
    categories = Category.objects.filter(tenant=tenant, branch=branch).annotate(
        product_count=Count('products', filter=Q(products__is_active=True, products__branch=branch))
    )

    # --- Faceted Filters Aggregation ---
    variants = ProductVariant.objects.filter(product__tenant=tenant, product__branch=branch, is_active=True)
    facet_data = list(variants.values_list('attributes', flat=True))
    available_brands = sorted(list(set(d.get('Brand') for d in facet_data if d and 'Brand' in d)))
    available_colors = sorted(list(set(d.get('Color') for d in facet_data if d and 'Color' in d)))
    available_sizes = sorted(list(set(d.get('Size') for d in facet_data if d and 'Size' in d)))

    # --- Filtering Logic ---
    # Category Filter
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # Price Range Filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try: products = products.filter(price__gte=float(min_price))
        except: pass
    if max_price:
        try: products = products.filter(price__lte=float(max_price))
        except: pass

    # Facet Filters
    selected_brands = request.GET.getlist('brand')
    selected_colors = request.GET.getlist('color')
    selected_sizes = request.GET.getlist('size')
    
    if selected_brands or selected_colors or selected_sizes:
        v_filter = Q()
        if selected_brands: v_filter &= Q(variants__attributes__Brand__in=selected_brands)
        if selected_colors: v_filter &= Q(variants__attributes__Color__in=selected_colors)
        if selected_sizes: v_filter &= Q(variants__attributes__Size__in=selected_sizes)
        products = products.filter(v_filter).distinct()

    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )
    else:
        # Sorting Logic
        sort_option = request.GET.get('sort', 'latest')
        if sort_option == 'price_low':
            products = products.order_by('price')
        elif sort_option == 'price_high':
            products = products.order_by('-price')
        else: # latest
            products = products.order_by('-created_at')

    # Recently Viewed Context
    recent_ids = request.session.get('recently_viewed', [])
    recently_viewed_products = Product.objects.filter(id__in=recent_ids, is_active=True)
    # Order them as they were viewed
    product_map = {str(p.id): p for p in recently_viewed_products}
    ordered_recent = [product_map[rid] for rid in recent_ids if rid in product_map]

    context = {
        'tenant': tenant,
        'branch': branch,
        'store_settings': store_settings,
        'products': products,
        'categories': categories,
        'current_sort': sort_option if not search_query else None,
        'current_min': min_price,
        'current_max': max_price,
        'available_brands': available_brands,
        'available_colors': available_colors,
        'available_sizes': available_sizes,
        'selected_brands': selected_brands,
        'selected_colors': selected_colors,
        'selected_sizes': selected_sizes,
        'cart_preview': cart_preview,
        'customer': customer,
        'recently_viewed': ordered_recent,
        'search_query': search_query,
    }
    return render(request, 'storefront/home.html', context)

@storefront_active_required
def product_detail(request, tenant_slug, branch_id, product_id):
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    product = get_object_or_404(Product, id=product_id, tenant=tenant, branch=branch, is_active=True)
    
    # Smart Recommendations (Frequently Bought Together)
    from main.services.intelligence_service import IntelligenceService
    intel_service = IntelligenceService(tenant, branch)
    smart_recommendations = intel_service.get_frequently_bought_together(product, limit=4)
    
    # Simple related products (same category) - as fallback if no smart ones
    if not smart_recommendations:
        related_products = Product.objects.filter(
            tenant=tenant, 
            branch=branch, 
            category=product.category, 
            is_active=True
        ).exclude(id=product.id)[:4]
    else:
        related_products = smart_recommendations

    # Recently Viewed Logic (Session based)
    recently_viewed = request.session.get('recently_viewed', [])
    prod_id_str = str(product.id)
    if prod_id_str in recently_viewed:
        recently_viewed.remove(prod_id_str)
    recently_viewed.insert(0, prod_id_str)
    request.session['recently_viewed'] = recently_viewed[:5] # Keep last 5

    # Reviews Context
    reviews = product.reviews.filter(is_visible=True).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = reviews.count()

    context = {
        'tenant': tenant,
        'branch': branch,
        'store_settings': store_settings,
        'product': product,
        'related_products': related_products,
        'is_smart_recom': bool(smart_recommendations),
        'cart_preview': cart_preview,
        'customer': customer,
        'categories': categories,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': review_count,
    }
    return render(request, 'storefront/product_detail.html', context)

@storefront_active_required
def store_cart(request, tenant_slug, branch_id):
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    cart = request.session.get('cart', {})
    
    cart_items = []
    total_amount = 0
    
    if cart:
        products = Product.objects.filter(id__in=cart.keys())
        for product in products:
            qty = cart.get(str(product.id), 0)
            if qty > 0:
                subtotal = product.price * qty
                total_amount += subtotal
                cart_items.append({
                    'product': product,
                    'quantity': qty,
                    'subtotal': subtotal
                })
    
    context = {
        'tenant': tenant,
        'branch': branch,
        'store_settings': store_settings,
        'cart_items': cart_items,
        'cart_items': cart_items,
        'total_amount': total_amount,
        'cart_preview': cart_preview,
        'customer': customer,
        'categories': categories,
    }
    return render(request, 'storefront/cart.html', context)

@storefront_active_required
def add_to_cart(request, tenant_slug, branch_id, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        try:
             qty = int(request.POST.get('quantity', 1))
             if qty < 1: qty = 1
        except (ValueError, TypeError):
             qty = 1
        
        current_qty = cart.get(str(product_id), 0)
        cart[str(product_id)] = current_qty + qty
        
        request.session['cart'] = cart
        messages.success(request, "Item added to cart")
        
    return redirect('store_home', tenant_slug=tenant_slug, branch_id=branch_id)

@storefront_active_required
def update_cart(request, tenant_slug, branch_id, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        try:
            qty = int(request.POST.get('quantity', 0))
            if qty < 0: qty = 0
        except (ValueError, TypeError):
            qty = 0
        
        if qty > 0:
            cart[str(product_id)] = qty
        else:
            if str(product_id) in cart:
                del cart[str(product_id)]
                
        request.session['cart'] = cart
    return redirect('store_cart', tenant_slug=tenant_slug, branch_id=branch_id)

@storefront_active_required
def remove_from_cart(request, tenant_slug, branch_id, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('store_cart', tenant_slug=tenant_slug, branch_id=branch_id)

from notifications.utils import trigger_new_order_notification
from utils.identifier_generator import generate_order_number

@storefront_active_required
def store_checkout(request, tenant_slug, branch_id):
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    cart = request.session.get('cart', {})
    
    if not cart:
        return redirect('store_home', tenant_slug=tenant_slug, branch_id=branch_id)
        
    # Calculate Total
    total_amount = 0
    products = Product.objects.filter(id__in=cart.keys())
    for product in products:
         qty = cart.get(str(product.id), 0)
         total_amount += product.price * qty

    # --- PAYMENT KEY LOGIC ---
    stripe_sk = getattr(django_settings, 'STRIPE_SECRET_KEY', '')
    stripe_pk = getattr(django_settings, 'STRIPE_PUBLIC_KEY', '')
    
    # If tenant has their own keys enabled, override
    if store_settings and store_settings.enable_stripe and store_settings.stripe_secret_key:
        stripe_sk = store_settings.stripe_secret_key
        stripe_pk = store_settings.stripe_public_key

    # Create Payment Intent for Stripe
    payment_intent_client_secret = None
    if stripe_sk and total_amount > 0:
        try:
            # Pass explicit api_key to support tenant isolation
            intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100), # Cents
                currency=branch.currency_symbol.replace('$', '').lower() or 'usd',
                metadata={'tenant_id': str(tenant.id), 'branch_id': str(branch.id)},
                api_key=stripe_sk 
            )
            payment_intent_client_secret = intent.client_secret
        except Exception as e:
            print(f"Stripe Error: {e}")
            # Fallback or show error? For now, we proceed (might default to Cash)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                name = form.cleaned_data['name']
                email = form.cleaned_data['email']
                phone = form.cleaned_data['phone']
                payment_method = form.cleaned_data['payment_method']
                address = form.cleaned_data['address']

                print(f"[Checkout] Processing order for {email}, payment: {payment_method}")

                # Loyalty Points specific validation
                if payment_method == 'loyalty_points':
                    if not customer:
                        messages.error(request, "You must be logged in to pay with loyalty points.")
                        return redirect('store_checkout', tenant_slug=tenant_slug, branch_id=branch_id)
                    
                    settings_crm, _ = CRMSettings.objects.get_or_create(tenant=tenant)
                    if settings_crm.redemption_rate <= 0:
                        messages.error(request, "Loyalty points redemption is currently unavailable.")
                        return redirect('store_checkout', tenant_slug=tenant_slug, branch_id=branch_id)
                    
                    required_points = total_amount / settings_crm.redemption_rate
                    if customer.loyalty_points < required_points:
                        messages.error(request, f"Insufficient points. You need {required_points:.0f} points (Balance: {customer.loyalty_points:.0f}).")
                        return redirect('store_checkout', tenant_slug=tenant_slug, branch_id=branch_id)

                with transaction.atomic():
                    if customer:
                        # Use existing profile if logged in
                        active_customer = customer
                    else:
                        # Guest or existing email check
                        active_customer = Customer.objects.filter(tenant=tenant, email=email).first()
                        if not active_customer:
                             active_customer = Customer.objects.create(
                                 tenant=tenant,
                                 branch=branch,
                                 name=name,
                                 email=email,
                                 phone=phone,
                                 address=address,
                                 customer_type='retail'
                             )
                    
                    order_number = generate_order_number(tenant)
                    
                    order = Order.objects.create(
                        tenant=tenant,
                        branch=branch,
                        customer=active_customer,
                        status='pending',
                        payment_method=payment_method,
                        ordering_type='online',
                        amount_paid=total_amount if payment_method in ['stripe', 'loyalty_points'] else 0,
                        order_number=order_number,
                        metadata={'address': address}
                    )

                    if payment_method == 'loyalty_points':
                        settings_crm, _ = CRMSettings.objects.get_or_create(tenant=tenant)
                        required_points = total_amount / settings_crm.redemption_rate
                        active_customer.loyalty_points -= required_points
                        active_customer.save()
                        
                        LoyaltyTransaction.objects.create(
                            tenant=tenant,
                            customer=active_customer,
                            order=order,
                            points=-required_points,
                            transaction_type='redeem',
                            description=f"Redeemed for Online Order #{order.order_number}"
                        )
                
                # Create Order Items
                final_total = 0
                for product in products:
                    qty = cart.get(str(product.id))
                    if qty:
                        # Update Stock
                        if product.stock_quantity >= qty:
                            product.stock_quantity -= qty
                            product.save()

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=qty,
                            price=product.price,
                            cost_price=product.cost_price
                        )
                        final_total += (product.price * qty)
                
                order.subtotal = final_total
                order.total_amount = final_total
                order.save()

                # CRM: Points earning (only if not paid with points)
                if active_customer and payment_method != 'loyalty_points':
                    active_customer.total_spend += final_total
                    settings_crm, _ = CRMSettings.objects.get_or_create(tenant=tenant)
                    points_earned = final_total * settings_crm.points_per_currency
                    if points_earned > 0:
                        active_customer.loyalty_points += points_earned
                        LoyaltyTransaction.objects.create(
                            tenant=tenant,
                            customer=active_customer,
                            order=order,
                            points=points_earned,
                            transaction_type='earn',
                            description=f"Earned from Online Order #{order.order_number}"
                        )
                    active_customer.calculate_tier()
                    active_customer.save()
                
                try:
                    trigger_new_order_notification(order)
                except Exception as e:
                    print(f"Failed to send notification: {e}")
                
                request.session['cart'] = {}
                
                # Mark abandoned cart as recovered
                AbandonedCart.objects.filter(email=email, tenant=tenant, is_recovered=False).update(is_recovered=True)
                
                print(f"[Checkout] Order {order.order_number} created successfully")
                return redirect('store_order_success', tenant_slug=tenant_slug, branch_id=branch_id, order_id=order.id)
            
            except Exception as e:
                print(f"[Checkout Error] {e}")
                import traceback
                traceback.print_exc()
                messages.error(request, f"An error occurred during checkout. Please try again or contact support.")
                return redirect('store_checkout', tenant_slug=tenant_slug, branch_id=branch_id)
        else:
            print(f"[Checkout] Form validation failed: {form.errors}")
            messages.error(request, "Please correct the errors in the form.")
            
    # Capture abandoned cart on checkout page load (if authenticated) or when email is provided
    if request.method == 'POST' and request.POST.get('email'):
        save_abandoned_cart(request, tenant, email=request.POST.get('email'))

    settings_crm, _ = CRMSettings.objects.get_or_create(tenant=tenant)
    context = {
        'tenant': tenant, 
        'branch': branch, 
        'store_settings': store_settings,
        'crm_settings': settings_crm,
        'total_amount': total_amount,
        'stripe_public_key': stripe_pk,
        'client_secret': payment_intent_client_secret,
        'cart_preview': cart_preview,
        'customer': customer,
        'categories': categories,
    }
    return render(request, 'storefront/checkout.html', context)

def store_order_success(request, tenant_slug, branch_id, order_id):
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    order = get_object_or_404(Order, id=order_id, tenant=tenant, branch=branch)
    return render(request, 'storefront/success.html', {
        'tenant': tenant, 
        'branch': branch, 
        'store_settings': store_settings, 
        'order': order,
        'cart_preview': cart_preview,
        'customer': customer,
        'categories': categories,
    })

from accounts.utils import merchant_only

@login_required
@merchant_only
def update_store_settings(request):
    # Enforce Admin Role
    if request.user.profile.role != 'admin':
        messages.error(request, "Access Denied: Only Admins can manage store settings.")
        return redirect('dashboard') 

    # Enforce 2FA
    if not request.user.profile.is_2fa_enabled:
        messages.warning(request, "Security Requirement: You must enable Two-Factor Authentication (2FA) to access Store Settings.")
        return redirect('setup_2fa')

    tenant = request.user.profile.tenant
    settings, created = StorefrontSettings.objects.get_or_create(tenant=tenant)
    
    if request.method == 'POST':
        form = StorefrontSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Store settings updated successfully.")
            return redirect('update_store_settings')
        else:
            print(f"DEBUG: Store Settings Form Errors: {form.errors}")
    else:
        form = StorefrontSettingsForm(instance=settings)
        
    return render(request, 'storefront/settings_form.html', {'form': form, 'store_settings': settings})


@storefront_active_required
def customer_login(request, tenant_slug, branch_id):
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    
    if request.user.is_authenticated:
        return redirect('store_home', tenant_slug=tenant_slug, branch_id=branch_id)

    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Check if user exists and password is correct (even if inactive)
            try:
                user_obj = User.objects.get(username=email)
                if user_obj.check_password(password):
                    # Check if email is verified
                    if not user_obj.is_active:
                        customer_profile = Customer.objects.filter(user=user_obj, tenant=tenant).first()
                        if customer_profile and not customer_profile.is_email_verified:
                            messages.warning(request, "Please verify your email address before logging in. Check your inbox for the verification link.")
                            return redirect('customer_login', tenant_slug=tenant_slug, branch_id=branch_id)
                    
                    # Proceed with normal authentication
                    user = authenticate(request, username=email, password=password)
                    if user is not None:
                        login(request, user)
                        messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                        return redirect('store_home', tenant_slug=tenant_slug, branch_id=branch_id)
                    else:
                        messages.error(request, "Invalid email or password.")
                else:
                    messages.error(request, "Invalid email or password.")
            except User.DoesNotExist:
                messages.error(request, "Invalid email or password.")
    else:
        form = CustomerLoginForm()
            
    return render(request, 'storefront/auth/login.html', {
        'tenant': tenant,
        'branch': branch,
        'store_settings': store_settings,
        'cart_preview': cart_preview,
        'categories': categories,
        'form': form,
    })

@storefront_active_required
def customer_register(request, tenant_slug, branch_id):
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    
    if request.user.is_authenticated:
        return redirect('store_home', tenant_slug=tenant_slug, branch_id=branch_id)

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            
            if User.objects.filter(username=email).exists():
                messages.error(request, "An account with this email already exists.")
            else:
                with transaction.atomic():
                    user = User.objects.create_user(username=email, email=email, password=password)
                    user.is_active = False  # Deactivate until email is verified
                    # Split name if possible
                    name_parts = name.split(' ', 1)
                    user.first_name = name_parts[0]
                    if len(name_parts) > 1:
                        user.last_name = name_parts[1]
                    user.save()
                    
                    # Create Customer profile
                    new_customer = Customer.objects.create(
                        tenant=tenant,
                        branch=branch,
                        user=user,
                        name=name,
                        email=email,
                        phone=phone,
                        customer_type='retail',
                        is_email_verified=False
                    )
                    
                    # Send verification email
                    try:
                        verification_url = request.build_absolute_uri(
                            f"/store/{tenant_slug}/{branch_id}/verify-email/{new_customer.email_verification_token}/"
                        )
                        
                        from django.core.mail import send_mail
                        from django.template.loader import render_to_string
                        from django.utils.html import strip_tags
                        
                        subject = f"Verify your email - {tenant.name}"
                        html_message = f"""
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #4F46E5;">Welcome to {tenant.name}!</h2>
                            <p>Hi {name},</p>
                            <p>Thank you for registering. Please verify your email address by clicking the button below:</p>
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{verification_url}" style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">Verify Email Address</a>
                            </div>
                            <p style="color: #666; font-size: 12px;">If the button doesn't work, copy and paste this link into your browser:</p>
                            <p style="color: #666; font-size: 12px; word-break: break-all;">{verification_url}</p>
                            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;" />
                            <p style="color: #999; font-size: 11px;">If you didn't create this account, please ignore this email.</p>
                        </div>
                        """
                        plain_message = strip_tags(html_message)
                        
                        send_mail(
                            subject=subject,
                            message=plain_message,
                            from_email=django_settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[email],
                            html_message=html_message,
                            fail_silently=False
                        )
                        
                        messages.success(request, f"Account created! Please check your email ({email}) to verify your account.")
                    except Exception as e:
                        print(f"Failed to send verification email: {e}")
                        messages.warning(request, "Account created, but we couldn't send the verification email. Please contact support.")
                    
                    return redirect('customer_login', tenant_slug=tenant_slug, branch_id=branch_id)
    else:
        form = CustomerRegistrationForm()
            
    return render(request, 'storefront/auth/register.html', {
        'tenant': tenant,
        'branch': branch,
        'store_settings': store_settings,
        'cart_preview': cart_preview,
        'categories': categories,
        'form': form,
    })

def customer_logout(request, tenant_slug, branch_id):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('store_home', tenant_slug=tenant_slug, branch_id=branch_id)

@login_required
@storefront_active_required
def customer_orders(request, tenant_slug, branch_id):
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    
    if not customer:
        messages.error(request, "Customer profile not found.")
        return redirect('store_home', tenant_slug=tenant_slug, branch_id=branch_id)
        
    orders = Order.objects.filter(customer=customer, tenant=tenant).order_by('-created_at')
    
    return render(request, 'storefront/account/orders.html', {
        'tenant': tenant,
        'branch': branch,
        'store_settings': store_settings,
        'cart_preview': cart_preview,
        'customer': customer,
        'orders': orders,
        'categories': categories,
    })

@login_required
@storefront_active_required
def customer_order_detail(request, tenant_slug, branch_id, order_id):
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    
    if not customer:
        messages.error(request, "Customer profile not found.")
        return redirect('store_home', tenant_slug=tenant_slug, branch_id=branch_id)
        
    order = get_object_or_404(Order, id=order_id, customer=customer, tenant=tenant)
    
    return render(request, 'storefront/account/order_detail.html', {
        'tenant': tenant,
        'branch': branch,
        'store_settings': store_settings,
        'cart_preview': cart_preview,
        'customer': customer,
        'order': order,
        'categories': categories,
    })

@login_required
@storefront_active_required
def customer_profile(request, tenant_slug, branch_id):
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    
    if not customer:
        messages.error(request, "Customer profile not found.")
        return redirect('store_home', tenant_slug=tenant_slug, branch_id=branch_id)
        
    if request.method == 'POST':
        # Check if this is a password change request
        if 'change_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # Validate current password
            if not request.user.check_password(current_password):
                messages.error(request, "Current password is incorrect.")
                return redirect('customer_profile', tenant_slug=tenant_slug, branch_id=branch_id)
            
            # Validate new passwords match
            if new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
                return redirect('customer_profile', tenant_slug=tenant_slug, branch_id=branch_id)
            
            # Validate password strength (minimum 8 characters)
            if len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
                return redirect('customer_profile', tenant_slug=tenant_slug, branch_id=branch_id)
            
            # Change password
            request.user.set_password(new_password)
            request.user.save()
            
            # Update session to prevent logout
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            
            messages.success(request, "Password changed successfully!")
            return redirect('customer_profile', tenant_slug=tenant_slug, branch_id=branch_id)
        else:
            # Regular profile update
            form = CustomerProfileForm(request.POST, instance=customer)
            if form.is_valid():
                customer = form.save()
                
                # Update User first name as well
                request.user.first_name = customer.name
                request.user.save()
                
                messages.success(request, "Profile updated successfully.")
                return redirect('customer_profile', tenant_slug=tenant_slug, branch_id=branch_id)
    else:
        form = CustomerProfileForm(instance=customer)
        
    return render(request, 'storefront/account/profile.html', {
        'tenant': tenant,
        'branch': branch,
        'store_settings': store_settings,
        'cart_preview': cart_preview,
        'customer': customer,
        'form': form,
        'categories': categories,
    })

@storefront_active_required
def api_search(request, tenant_slug, branch_id):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    tenant = get_object_or_404(Tenant, subdomain=tenant_slug)
    branch = get_object_or_404(Branch, id=branch_id, tenant=tenant)
    
    products = Product.objects.filter(
        tenant=tenant, 
        branch=branch, 
        is_active=True
    ).filter(
        Q(name__icontains=query)
    )[:5]
    
    results = []
    for p in products:
        results.append({
            'id': str(p.id),
            'name': p.name,
            'price': float(p.price),
            'image': p.image.url if p.image else None,
            'url': f"/store/{tenant_slug}/{branch_id}/product/{p.id}/"
        })
        
    return JsonResponse({'results': results})
@login_required
@storefront_active_required
def toggle_wishlist(request, tenant_slug, branch_id, product_id):
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    if not customer:
        return JsonResponse({'status': 'error', 'message': 'Profile required'})
        
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = Wishlist.objects.filter(customer=customer, product=product).first()
    
    if wishlist_item:
        wishlist_item.delete()
        added = False
    else:
        Wishlist.objects.create(customer=customer, product=product)
        added = True
        
    return JsonResponse({'status': 'success', 'added': added})

@login_required
@storefront_active_required
def customer_wishlist(request, tenant_slug, branch_id):
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    if not customer:
        return redirect('store_home', tenant_slug=tenant_slug, branch_id=branch_id)
        
    wishlist_items = Wishlist.objects.filter(customer=customer).select_related('product')
    
    return render(request, 'storefront/account/wishlist.html', {
        'tenant': tenant,
        'branch': branch,
        'store_settings': store_settings,
        'cart_preview': cart_preview,
        'customer': customer,
        'categories': categories,
        'wishlist_items': wishlist_items,
    })

@login_required
@storefront_active_required
def submit_review(request, tenant_slug, branch_id, product_id):
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    if not customer:
        messages.error(request, "Please complete your profile to leave a review.")
        return redirect('customer_profile', tenant_slug=tenant_slug, branch_id=branch_id)
        
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.tenant = tenant
            review.product = product
            review.customer = customer
            review.save()
            messages.success(request, "Thank you for your review!")
        else:
            messages.error(request, "There was an error with your review.")
            
    return redirect('store_product_detail', tenant_slug=tenant_slug, branch_id=branch_id, product_id=product_id)

@storefront_active_required
def apply_coupon(request, tenant_slug, branch_id):
    if request.method == 'POST':
        form = CouponApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code'].strip().upper()
            tenant = get_object_or_404(Tenant, subdomain=tenant_slug)
            
            from django.utils import timezone
            coupon = Coupon.objects.filter(
                code=code,
                tenant=tenant,
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            ).first()
            
            if coupon:
                if coupon.used_count < coupon.usage_limit:
                    request.session['applied_coupon'] = {
                        'code': coupon.code,
                        'discount_type': coupon.discount_type,
                        'value': float(coupon.value),
                        'min_purchase': float(coupon.min_purchase)
                    }
                    messages.success(request, f"Coupon '{code}' applied successfully!")
                else:
                    messages.error(request, "This coupon has reached its usage limit.")
            else:
                messages.error(request, "Invalid or expired coupon code.")
            
    return redirect('store_cart', tenant_slug=tenant_slug, branch_id=branch_id)

@storefront_active_required
def remove_coupon(request, tenant_slug, branch_id):
    if 'applied_coupon' in request.session:
        del request.session['applied_coupon']
        messages.success(request, "Coupon removed.")
    return redirect('store_cart', tenant_slug=tenant_slug, branch_id=branch_id)

@storefront_active_required
def subscribe_newsletter(request, tenant_slug, branch_id):
    tenant = get_object_or_404(Tenant, subdomain=tenant_slug)
    if request.method == 'POST':
        form = NewsletterSubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            sub, created = NewsletterSubscription.objects.get_or_create(
                tenant=tenant,
                email=email
            )
            if created:
                messages.success(request, "Thank you for subscribing to our newsletter!")
            else:
                messages.info(request, "You are already subscribed to our newsletter.")
        else:
            messages.error(request, "Invalid email address.")
            
    return redirect(request.META.get('HTTP_REFERER', 'store_home'))

@storefront_active_required
def track_order(request, tenant_slug, branch_id):
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    order = None
    error = None
    
    if request.method == 'POST':
        form = TrackOrderForm(request.POST)
        if form.is_valid():
            order_id = form.cleaned_data['order_id']
            try:
                order = Order.objects.get(id=order_id, tenant=tenant)
            except (Order.DoesNotExist, ValueError):
                error = "Order not found. Please check your ID."
        else:
            error = "Please enter a valid Order ID."
            
    return render(request, 'storefront/track_order.html', {
        'tenant': tenant,
        'branch': branch,
        'store_settings': store_settings,
        'cart_preview': cart_preview,
        'customer': customer,
        'categories': categories,
        'order': order,
        'error': error,
    })

def recover_cart(request, cart_id):
    """Restore an abandoned cart from recovery email link."""
    try:
        abandoned_cart = get_object_or_404(AbandonedCart, id=cart_id, is_recovered=False)
        
        # Restore the cart to session
        request.session['cart'] = abandoned_cart.cart_data
        
        # Mark as recovered
        abandoned_cart.is_recovered = True
        abandoned_cart.save()
        
        # Get tenant and branch from the abandoned cart to redirect properly
        tenant = abandoned_cart.tenant
        store_settings = StorefrontSettings.objects.filter(tenant=tenant).first()
        
        if store_settings and store_settings.default_branch:
            branch = store_settings.default_branch
        else:
            # Fallback to first branch
            branch = tenant.branches.first()
        
        if not branch:
            messages.error(request, "Unable to restore cart. Please contact support.")
            return redirect('landing')
        
        messages.success(request, "Your cart has been restored! Complete your purchase now.")
        return redirect('store_cart', tenant_slug=tenant.subdomain, branch_id=branch.id)
        
    except Exception as e:
        messages.error(request, "This recovery link is invalid or has expired.")
        return redirect('landing')

@storefront_active_required
def store_about(request, tenant_slug, branch_id):
    """About Us page."""
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    return render(request, 'storefront/about.html', {
        'tenant': tenant,
        'branch': branch,
        'store_settings': store_settings,
        'cart_preview': cart_preview,
        'customer': customer,
        'categories': categories,
    })

@storefront_active_required
def store_privacy(request, tenant_slug, branch_id):
    """Privacy Policy page."""
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    return render(request, 'storefront/privacy.html', {
        'tenant': tenant,
        'branch': branch,
        'store_settings': store_settings,
        'cart_preview': cart_preview,
        'customer': customer,
        'categories': categories,
    })

@storefront_active_required
def store_terms(request, tenant_slug, branch_id):
    """Terms of Service page."""
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    return render(request, 'storefront/terms.html', {
        'tenant': tenant,
        'branch': branch,
        'store_settings': store_settings,
        'cart_preview': cart_preview,
        'customer': customer,
        'categories': categories,
    })

@storefront_active_required
def store_contact(request, tenant_slug, branch_id):
    """Contact Support page with form."""
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message_text = form.cleaned_data['message']
            
            # Here you would typically send an email
            # For now we just log it or show success
            messages.success(request, "Thank you for your message! We will get back to you soon.")
            return redirect('store_contact', tenant_slug=tenant_slug, branch_id=branch_id)
    else:
        form = ContactForm()
            
    return render(request, 'storefront/contact.html', {
        'tenant': tenant,
        'branch': branch,
        'store_settings': store_settings,
        'cart_preview': cart_preview,
        'categories': categories,
        'form': form,
    })

@storefront_active_required
def store_shipping(request, tenant_slug, branch_id):
    """Shipping & Pickup information page."""
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    return render(request, 'storefront/shipping.html', {
        'tenant': tenant,
        'branch': branch,
        'store_settings': store_settings,
        'cart_preview': cart_preview,
        'customer': customer,
        'categories': categories,
    })

@storefront_active_required
def store_returns(request, tenant_slug, branch_id):
    """Returns & Exchanges policy page."""
    tenant, branch, store_settings, cart_preview, customer, categories = get_context(request, tenant_slug, branch_id)
    return render(request, 'storefront/returns.html', {
        'tenant': tenant,
        'branch': branch,
        'store_settings': store_settings,
        'cart_preview': cart_preview,
        'customer': customer,
        'categories': categories,
    })

def verify_email(request, tenant_slug, branch_id, token):
    """Handle email verification from the link sent to customer."""
    tenant = get_object_or_404(Tenant, subdomain=tenant_slug)
    branch = get_object_or_404(Branch, id=branch_id, tenant=tenant)
    
    try:
        customer = Customer.objects.get(
            email_verification_token=token,
            tenant=tenant
        )
        
        if customer.is_email_verified:
            messages.info(request, "Your email is already verified. You can log in now.")
        else:
            # Mark as verified
            customer.is_email_verified = True
            customer.save(update_fields=['is_email_verified'])
            
            # Activate the user account
            if customer.user:
                customer.user.is_active = True
                customer.user.save(update_fields=['is_active'])
            
            messages.success(request, "Email verified successfully! You can now log in to your account.")
        
        return redirect('customer_login', tenant_slug=tenant_slug, branch_id=branch_id)
        
    except Customer.DoesNotExist:
        messages.error(request, "Invalid verification link. Please contact support if you need help.")
        return redirect('store_home', tenant_slug=tenant_slug, branch_id=branch_id)

