"""
Test script to simulate a request through the subscription middleware
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from billing.middleware import SubscriptionMiddleware
from accounts.models import UserProfile
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(name)s - %(message)s'
)

User = get_user_model()
factory = RequestFactory()

# Get a user with a tenant
try:
    profile = UserProfile.objects.select_related('user', 'tenant').filter(
        tenant__isnull=False
    ).first()
    
    if not profile:
        print("No user profiles with tenants found!")
        exit(1)
    
    user = profile.user
    print(f"\nTesting with user: {user.username}")
    print(f"Tenant: {profile.tenant.name}")
    print(f"Is superuser: {user.is_superuser}")
    print("\n" + "=" * 70)
    
    # Create a mock request to dashboard
    request = factory.get('/dashboard/')
    request.user = user
    
    # Create middleware instance
    middleware = SubscriptionMiddleware(lambda r: type('Response', (), {'status_code': 200})())
    
    # Process the request
    print("\nProcessing request to /dashboard/...")
    print("=" * 70)
    response = middleware(request)
    
    print("\n" + "=" * 70)
    print(f"Response status: {response.status_code if hasattr(response, 'status_code') else 'Redirect'}")
    if hasattr(response, 'url'):
        print(f"Redirect URL: {response.url}")
    print("=" * 70)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
