from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Plan, Subscription, PaymentGatewayConfig
from .forms import PaymentProviderForm

def pricing_view(request):
    """
    Public pricing page or internally for upgrading.
    """
    # Default to standard plans for public view
    tenant_type = request.GET.get('type', 'standard')
    current_plan_id = None
    
    # Currency handling
    currency = request.GET.get('currency')
    if currency in ['USD', 'GHS']:
        request.session['currency'] = currency
    
    active_currency = request.session.get('currency', 'GHS')
    
    # If logged in, force tenant_type from their profile
    if request.user.is_authenticated and getattr(request.user, 'profile', None) and request.user.profile.tenant:
        tenant = request.user.profile.tenant
        tenant = request.user.profile.tenant
        try:
            subscription = tenant.subscription
            if subscription.plan:
                current_plan_id = subscription.plan.id
        except Subscription.DoesNotExist:
            pass

    # Filter plans
    plans = Plan.objects.filter(is_active=True).order_by('price')
    
    # Active Currency handling
    active_currency = request.session.get('currency', 'GHS')

    context = {
        'plans': plans,
        'current_plan_id': current_plan_id,
        'active_currency': active_currency
    }
    return render(request, 'billing/pricing.html', context)

@login_required
def subscription_required_view(request):
    """
    Display subscription required page for users without active subscriptions.
    """
    tenant = None
    subscription_status = 'No subscription'
    
    if hasattr(request.user, 'profile') and request.user.profile.tenant:
        tenant = request.user.profile.tenant
        try:
            subscription = tenant.subscription
            subscription_status = subscription.get_status_display()
        except Subscription.DoesNotExist:
            subscription_status = 'No subscription'
    
    context = {
        'tenant': tenant,
        'subscription_status': subscription_status,
    }
    return render(request, 'billing/subscription_required.html', context)


@login_required
def checkout_view(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    
    # Fetch active payment gateways
    active_gateways = PaymentGatewayConfig.objects.filter(is_active=True)
    
    return render(request, 'billing/checkout.html', {
        'plan': plan,
        'active_gateways': active_gateways
    })

@login_required
def process_payment(request, plan_id):
    if request.method != 'POST':
        return redirect('checkout', plan_id=plan_id)
        
    plan = get_object_or_404(Plan, id=plan_id)
    tenant = request.user.profile.tenant
    
    form = PaymentProviderForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Invalid payment provider selected.")
        return redirect('checkout', plan_id=plan_id)
    
    provider = form.cleaned_data['payment_provider']
    
    # Validate that the selected provider is active
    if not PaymentGatewayConfig.objects.filter(slug=provider, is_active=True).exists():
        from django.contrib import messages
        messages.error(request, f"The selected payment provider ({provider}) is currently disabled. Please choose another method.")
        return redirect('checkout', plan_id=plan_id)
    
    # Handle Free Trial (no payment required)
    if plan.price == 0:
        from datetime import timedelta
        from django.utils import timezone
        
        # Activate free trial subscription
        Subscription.objects.update_or_create(
            tenant=tenant,
            defaults={
                'plan': plan,
                'status': 'trialing',
                'current_period_end': timezone.now() + timedelta(days=plan.trial_days),
                'cancel_at_period_end': False
            }
        )
        return redirect('payment_success')
    
    if provider == 'stripe':
        import stripe
        from django.conf import settings
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Map interval to Stripe format
        interval_map = {
            'monthly': 'month',
            '6-month': 'month',
            'yearly': 'year'
        }
        stripe_interval = interval_map.get(plan.interval, 'month')
        interval_count = 6 if plan.interval == '6-month' else 1
        
        try:
            # Create Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(plan.price * 100),  # Convert to cents
                        'product_data': {
                            'name': f'{plan.name} Plan',
                            'description': plan.description,
                        },
                        'recurring': {
                            'interval': stripe_interval,
                            'interval_count': interval_count,
                        },
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=request.build_absolute_uri(reverse('payment_success')) + f'?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
                client_reference_id=str(tenant.id),
                subscription_data={
                    'trial_period_days': plan.trial_days,
                },
                metadata={
                    'plan_id': str(plan.id),
                    'tenant_id': str(tenant.id),
                }
            )
            return redirect(checkout_session.url)
        except Exception as e:
            # Log error and redirect back
            print(f"Stripe error: {e}")
            return redirect('checkout', plan_id=plan_id)
            
    elif provider == 'paystack':
        import requests
        from django.conf import settings
        
        # Use regional GHS pricing from database
        amount_in_ghs = float(plan.price_ghs)
        
        # Initialize Paystack payment
        url = 'https://api.paystack.co/transaction/initialize'
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        }
        data = {
            'email': request.user.email,
            'amount': int(amount_in_ghs * 100),  # Convert to pesewas (GHS cents)
            'currency': 'GHS',
            'callback_url': request.build_absolute_uri(reverse('paystack_callback')),
            'metadata': {
                'plan_id': str(plan.id),
                'tenant_id': str(tenant.id),
                'plan_name': plan.name,
                'original_price_usd': float(plan.price),
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            response_data = response.json()
            
            if response_data.get('status'):
                authorization_url = response_data['data']['authorization_url']
                return redirect(authorization_url)
            else:
                print(f"Paystack error: {response_data}")
                return redirect('checkout', plan_id=plan_id)
        except Exception as e:
            print(f"Paystack error: {e}")
            return redirect('checkout', plan_id=plan_id)
            
    elif provider == 'paypal':
        # PayPal integration would go here
        # For now, redirect back to checkout
        return redirect('checkout', plan_id=plan_id)
        
    return redirect('checkout', plan_id=plan_id)

@login_required
def payment_success(request):
    """Handle successful payment redirect and verify activation"""
    session_id = request.GET.get('session_id')
    
    if session_id:
        import stripe
        from django.conf import settings
        from accounts.models import Tenant
        from datetime import timedelta
        from django.utils import timezone
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            # Only process if it was successful
            if session.status == 'complete' or session.payment_status == 'paid':
                tenant_id = session.metadata.get('tenant_id')
                plan_id = session.metadata.get('plan_id')
                
                if tenant_id and plan_id:
                    try:
                        tenant = Tenant.objects.get(id=tenant_id)
                        plan = Plan.objects.get(id=plan_id)
                        
                        # Calculate period end
                        if plan.interval == 'monthly':
                            period_end = timezone.now() + timedelta(days=30)
                        elif plan.interval == '6-month':
                            period_end = timezone.now() + timedelta(days=180)
                        elif plan.interval == 'yearly':
                            period_end = timezone.now() + timedelta(days=365)
                        else:
                            period_end = timezone.now() + timedelta(days=30)
                        
                        # Activate immediately (webhook will also do this, which is fine)
                        Subscription.objects.update_or_create(
                            tenant=tenant,
                            defaults={
                                'plan': plan,
                                'status': 'active',
                                'stripe_subscription_id': session.get('subscription'),
                                'current_period_end': period_end,
                                'cancel_at_period_end': False
                            }
                        )
                    except (Tenant.DoesNotExist, Plan.DoesNotExist):
                        pass
        except Exception as e:
            print(f"Stripe verification error: {e}")

    return render(request, 'billing/success.html', {'session_id': session_id})

@login_required
def payment_cancel(request):
    """Handle cancelled payment"""
    return render(request, 'billing/cancel.html')

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    import stripe
    from django.conf import settings
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET if hasattr(settings, 'STRIPE_WEBHOOK_SECRET') else ''
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Get tenant and plan from metadata
        tenant_id = session.get('metadata', {}).get('tenant_id')
        plan_id = session.get('metadata', {}).get('plan_id')
        
        if tenant_id and plan_id:
            from accounts.models import Tenant
            from datetime import timedelta
            from django.utils import timezone
            
            try:
                tenant = Tenant.objects.get(id=tenant_id)
                plan = Plan.objects.get(id=plan_id)
                
                # Calculate period end based on plan interval
                if plan.interval == 'monthly':
                    period_end = timezone.now() + timedelta(days=30)
                elif plan.interval == '6-month':
                    period_end = timezone.now() + timedelta(days=180)
                elif plan.interval == 'yearly':
                    period_end = timezone.now() + timedelta(days=365)
                else:
                    period_end = timezone.now() + timedelta(days=30)  # Default to monthly
                
                # Activate subscription
                Subscription.objects.update_or_create(
                    tenant=tenant,
                    defaults={
                        'plan': plan,
                        'status': 'active',
                        'stripe_subscription_id': session.get('subscription'),
                        'current_period_end': period_end,
                        'cancel_at_period_end': False
                    }
                )
            except (Tenant.DoesNotExist, Plan.DoesNotExist) as e:
                print(f"Webhook error: Tenant or Plan not found. {e}")
                return HttpResponse(status=400)
            except Exception as e:
                print(f"Webhook error: {e}")
                return HttpResponse(status=500)
    
    return HttpResponse(status=200)

@csrf_exempt
def paystack_webhook(request):
    """Handle Paystack webhook events"""
    import hmac
    import hashlib
    from django.conf import settings
    
    # Verify webhook signature
    paystack_signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
    if paystack_signature:
        hash_value = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
            request.body,
            hashlib.sha512
        ).hexdigest()
        
        if hash_value != paystack_signature:
            return HttpResponse(status=400)
    
    try:
        data = json.loads(request.body)
        event = data.get('event')
        
        if event == 'charge.success':
            transaction_data = data.get('data', {})
            metadata = transaction_data.get('metadata', {})
            
            # Paystack sometimes returns metadata as a string
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except:
                    metadata = {}
            
            tenant_id = metadata.get('tenant_id')
            plan_id = metadata.get('plan_id')
            
            if tenant_id and plan_id:
                from accounts.models import Tenant
                from datetime import timedelta
                from django.utils import timezone
                
                try:
                    tenant = Tenant.objects.get(id=tenant_id)
                    plan = Plan.objects.get(id=plan_id)
                    
                    # Calculate period end based on plan interval
                    if plan.interval == 'monthly':
                        period_end = timezone.now() + timedelta(days=30)
                    elif plan.interval == '6-month':
                        period_end = timezone.now() + timedelta(days=180)
                    elif plan.interval == 'yearly':
                        period_end = timezone.now() + timedelta(days=365)
                    else:
                        period_end = timezone.now() + timedelta(days=30)  # Default to monthly
                    
                    # Activate subscription
                    Subscription.objects.update_or_create(
                        tenant=tenant,
                        defaults={
                            'plan': plan,
                            'status': 'active',
                            'current_period_end': period_end,
                            'cancel_at_period_end': False
                        }
                    )
                except (Tenant.DoesNotExist, Plan.DoesNotExist) as e:
                    print(f"Paystack webhook error: Tenant or Plan not found. {e}")
                except Exception as e:
                    print(f"Paystack webhook error: {e}")
    except Exception as e:
        print(f"Paystack webhook error: {e}")
        return HttpResponse(status=400)
    
    return HttpResponse(status=200)

@login_required
def paystack_callback(request):
    """Handle Paystack payment callback"""
    reference = request.GET.get('reference')
    
    if reference:
        import requests
        from django.conf import settings
        
        # Verify transaction
        url = f'https://api.paystack.co/transaction/verify/{reference}'
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        }
        
        try:
            response = requests.get(url, headers=headers)
            response_data = response.json()
            
            if response_data.get('status') and response_data['data']['status'] == 'success':
                # Extract metadata to activate subscription
                transaction_data = response_data['data']
                metadata = transaction_data.get('metadata', {})
                
                # Paystack sometimes returns metadata as a string
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                tenant_id = metadata.get('tenant_id')
                plan_id = metadata.get('plan_id')
                
                if tenant_id and plan_id:
                    from accounts.models import Tenant
                    from datetime import timedelta
                    from django.utils import timezone
                    
                    try:
                        tenant = Tenant.objects.get(id=tenant_id)
                        plan = Plan.objects.get(id=plan_id)
                        
                        # Calculate period end based on plan interval
                        if plan.interval == 'monthly':
                            period_end = timezone.now() + timedelta(days=30)
                        elif plan.interval == '6-month':
                            period_end = timezone.now() + timedelta(days=180)
                        elif plan.interval == 'yearly':
                            period_end = timezone.now() + timedelta(days=365)
                        else:
                            period_end = timezone.now() + timedelta(days=30)
                        
                        # Activate subscription
                        Subscription.objects.update_or_create(
                            tenant=tenant,
                            defaults={
                                'plan': plan,
                                'status': 'active',
                                'current_period_end': period_end,
                                'cancel_at_period_end': False
                            }
                        )
                    except (Tenant.DoesNotExist, Plan.DoesNotExist) as e:
                        print(f"Paystack verification error: Tenant or Plan not found. {e}")
                
                return render(request, 'billing/success.html', {'reference': reference})
            else:
                print(f"Paystack verification failed: {response_data}")
        except Exception as e:
            print(f"Paystack verification error: {e}")
    
    return render(request, 'billing/cancel.html')
