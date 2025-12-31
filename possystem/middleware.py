from accounts.models import Tenant
from django.http import Http404
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

class SubdomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower()
        domain_parts = host.split('.')
        
        request.tenant = None
        
        # Logic to extract subdomain
        # Assumes structure: [subdomain].[domain].[tld] (3 parts) or [subdomain].localhost (2 parts for local testing if configured)
        # If accessing via IP or plain localhost, it's considered public.
        
        if len(domain_parts) > 2:
            subdomain = domain_parts[0]
        elif len(domain_parts) == 2 and domain_parts[1] == 'localhost': # Special case for subdomain.localhost
            subdomain = domain_parts[0]
        else:
            subdomain = None

        if subdomain and subdomain != 'www':
            try:
                request.tenant = Tenant.objects.get(subdomain=subdomain)
            except Tenant.DoesNotExist:
                # If a subdomain is accessed but doesn't exist, we can return 404
                # allowing the main site to handle 'www' or root.
                raise Http404("Tenant not found")
        
        response = self.get_response(request)
        return response

class TwoFAMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # DEBUG: Trace 2FA logic
            # print(f"DEBUG: 2FA Middleware - User: {request.user}, Path: {request.path}")
            
            # Check if user has profile first (admins might not)
            if hasattr(request.user, 'profile') and request.user.profile and request.user.profile.is_2fa_enabled:
                is_verified = request.session.get('is_2fa_verified', False)
                # print(f"DEBUG: 2FA Enabled. Verified: {is_verified}")
                
                if not is_verified:
                    current_path = request.path
                    auth_paths = [
                        reverse('verify_2fa'), 
                        reverse('logout'), 
                        reverse('setup_2fa'),
                        '/admin/' # Allow admin access without 2FA for now or handle separately
                    ]
                    
                    # TEMPORARY EXEMPTION FOR POS TO DEBUG SESSION ISSUE
                    # Also exempt API calls to prevent 302 redirects breaking Ajax/JSON
                    if '/pos/' in current_path or current_path.startswith('/api/') or '/pos/checkout/' in current_path:
                        # We still want to log this oddity
                        # print(f"DEBUG: Allowing access to POS/API despite 2FA unverified: {current_path}")
                        pass
                    elif current_path not in auth_paths and not current_path.startswith('/static/'):
                        print(f"DEBUG: Redirecting to verify_2fa from {current_path}")
                        return redirect(f"{reverse('verify_2fa')}?next={current_path}")

        response = self.get_response(request)
        return response
