import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Tenant, UserProfile
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

@pytest.mark.django_db
class TestTenantLifecycle:
    """
    Smoke test covering the entire lifecycle of a merchant:
    1. Registration (Multi-step)
    2. Account Activation (Email Verification)
    3. Login & Dashboard Access
    """
    
    def test_merchant_onboarding_flow(self, client):
        # --- STEP 1: User Details ---
        signup_url = reverse('signup')
        user_data = {
            'username': 'newmerchant',
            'email': 'merchant@puxbay.com',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!',
            'step': '1'
        }
        
        response = client.post(signup_url, user_data)
        assert response.status_code == 200, f"Step 1 failed: {response.content.decode()}"
        assert 'signup_user_data' in client.session
        
        # --- STEP 2: Company Details ---
        company_data = {
            'company_name': 'Green Grocers',
            'subdomain': 'greengrocers',
            'step': '2'
        }
        
        response = client.post(signup_url, company_data)
        assert response.status_code == 302, f"Step 2 failed: {response.content.decode()}"
        assert response.url == reverse('verification_sent')
        
        # Verify db state (inactive user)
        user = User.objects.get(username='newmerchant')
        assert user.is_active is False
        
        tenant = Tenant.objects.get(subdomain='greengrocers')
        assert tenant.name == 'Green Grocers'
        
        # --- STEP 3: Email Verification ---
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activate_url = reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
        
        response = client.get(activate_url)
        assert response.status_code == 302, f"Activation failed: {response.content.decode()}"
        
        user.refresh_from_db()
        assert user.is_active is True
        
        # --- STEP 4: Login ---
        login_url = reverse('login')
        login_data = {
            'username': 'newmerchant',
            'password': 'StrongPassword123!'
        }
        
        response = client.post(login_url, login_data)
        assert response.status_code == 302, f"Login failed: {response.content.decode()}"
        
        # --- STEP 5: Dashboard Access ---
        # Note: In a multi-tenant setup, we usually need to ensure the request 
        # is hitting the correct subdomain. For simple unit/integration tests, 
        # we often use the public schema or mock the tenant middleware.
        # Here we verify the user is authenticated.
        assert '_auth_user_id' in client.session
