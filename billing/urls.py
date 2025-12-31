from django.urls import path
from . import views

urlpatterns = [
    path('pricing/', views.pricing_view, name='pricing'),
    path('subscription-required/', views.subscription_required_view, name='subscription_required'),
    path('checkout/<uuid:plan_id>/', views.checkout_view, name='checkout'),
    path('checkout/<uuid:plan_id>/process/', views.process_payment, name='process_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
    path('paystack/callback/', views.paystack_callback, name='paystack_callback'),
]

