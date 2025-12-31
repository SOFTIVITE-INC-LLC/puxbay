from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import TenantRegistrationForm, UserRegistrationForm, BranchForm, StaffCreationForm
from .models import Tenant, UserProfile, Branch
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.db import transaction
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

def register_tenant(request):
    # Check for signup type in GET or session
    signup_type = request.GET.get('type')
    if signup_type:
        request.session['signup_type'] = signup_type
    else:
        signup_type = request.session.get('signup_type', 'retailer')

    step = int(request.POST.get('step', 1))
    
    # Initialize forms with None
    user_form = None
    tenant_form = None

    if request.method == 'POST':
        if step == 1:
            user_form = UserRegistrationForm(request.POST)
            if user_form.is_valid():
                # Store step 1 data in session
                request.session['signup_user_data'] = user_form.cleaned_data
                # Prepare step 2
                step = 2
                tenant_form = TenantRegistrationForm()
        
        elif step == 2:
            tenant_form = TenantRegistrationForm(request.POST)
            user_data = request.session.get('signup_user_data')
            
            if not user_data:
                # Session expired or missing data, restart
                return redirect('signup')

            if tenant_form.is_valid():
                try:
                    with transaction.atomic():
                        # Finalize registration
                        
                        # 1. Create User
                        user = User(
                            username=user_data['username'],
                            email=user_data['email'],
                            is_active=False # Deactivate until email verified
                        )
                        user.set_password(user_data['password'])
                        user.save()
                        
                        # 2. Create Tenant
                        tenant = tenant_form.save() # Form now correctly maps 'name' field

                        # Create Domain
                        from .models import Domain
                        domain_base = request.get_host().split(':')[0]
                        # Handling generic "localhost" implies we want subdomains like "tenant.localhost"
                        # If we are on public domain "example.com", we want "tenant.example.com"
                        full_domain = f"{tenant.subdomain}.{domain_base}"
                        
                        Domain.objects.create(
                            domain=full_domain,
                            tenant=tenant,
                            is_primary=True
                        )
                        
                        # 3. Create Profile
                        UserProfile.objects.create(
                            user=user,
                            tenant=tenant,
                            role='admin'
                        )

                        # Send Verification Email
                        try:
                            token = default_token_generator.make_token(user)
                            uid = urlsafe_base64_encode(force_bytes(user.pk))
                            activation_link = request.build_absolute_uri(
                                reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
                            )

                            # HTML Email Content
                            html_message = render_to_string('emails/verify_email.html', {
                                'user': user,
                                'tenant_name': tenant.name,
                                'activation_link': activation_link,
                            })
                            plain_message = strip_tags(html_message)
                            
                            send_mail(
                                subject=f"Verify your email for {tenant.name}",
                                message=plain_message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[user.email],
                                html_message=html_message,
                                fail_silently=False
                            )
                        except Exception as e:
                            print(f"Failed to send verification email: {e}")
                            # Clean up user if email fails? Or just let them retry/resend?
                            # For now, we proceed but they might be stuck if email didn't go out.
                        
                        # 4. Cleanup Session
                        signup_type = request.session.get('signup_type', 'retailer')
                        if 'signup_user_data' in request.session:
                            del request.session['signup_user_data']
                        if 'signup_type' in request.session:
                            del request.session['signup_type']

                        # DO NOT LOGIN - Redirect to detailed 'Check Email' page
                        return redirect('verification_sent')
                except Exception as e:
                    # If any error occurs (e.g. IntegrityError even inside transaction if triggered oddly, 
                    # or some other save error), add error to form and let user retry.
                    # Since we are in atomic block, User creation is rolled back.
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Registration failed for user {user_data.get('username', 'unknown')}: {str(e)}", exc_info=True)
                    tenant_form.add_error(None, f"Registration failed: {str(e)}")

                
            # If step 2 invalid, re-render step 2 (user_form not needed for display but maybe for context?)
            # We don't need to re-render user_form errors if we are on step 2.

    else:
        # GET request, start at step 1
        step = 1
        user_form = UserRegistrationForm()

    # Context preparation
    context = {
        'step': step,
        'user_form': user_form if step == 1 else None,
        'tenant_form': tenant_form if step == 2 else None,
        'signup_type': signup_type
    }
    
    return render(request, 'accounts/signup.html', context)

@login_required
def branch_list(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return render(request, 'base.html')

    branches = Branch.objects.filter(tenant=profile.tenant)
    return render(request, 'accounts/branch_list.html', {'branches': branches})

@login_required
def branch_create(request):
    from billing.utils import check_branch_limit
    from django.contrib import messages
    
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return redirect('/')

    # Check branch limit
    can_create, current_count, max_allowed = check_branch_limit(profile.tenant)
    if not can_create:
        messages.error(request, f'Branch limit reached! Your plan allows {max_allowed} branch(es). Upgrade to add more.')
        return redirect('branch_list')

    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            branch = form.save(commit=False)
            branch.tenant = profile.tenant
            branch.save()
            return redirect('branch_list')
    else:
        form = BranchForm()
    
    return render(request, 'accounts/branch_form.html', {'form': form, 'title': 'Add New Branch'})

@login_required
def branch_update(request, pk):
    try:
        profile = request.user.profile
        if profile.role == 'sales':
            return redirect('branch_dashboard', branch_id=pk)
    except UserProfile.DoesNotExist:
        return redirect('/')

    branch = get_object_or_404(Branch, pk=pk, tenant=profile.tenant)
    old_instance = Branch.objects.get(pk=pk) # Fresh copy for diff
    
    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            from accounts.services.audit_service import AuditService
            changes = AuditService.get_field_diff(old_instance, branch)
            form.save()
            
            if changes:
                AuditService.log_action(
                    request, 
                    'update', 
                    f"Updated branch details for {branch.name}",
                    target_model='Branch',
                    target_object_id=branch.id,
                    changes=changes
                )
            return redirect('branch_list')
    else:
        form = BranchForm(instance=branch)
    
    return render(request, 'accounts/branch_form.html', {'form': form, 'title': 'Edit Branch'})

@login_required
def staff_list(request):
    try:
        profile = request.user.profile
        if profile.role != 'admin':
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        return redirect('landing')

    staff_profiles = UserProfile.objects.filter(tenant=profile.tenant).exclude(role='admin')
    return render(request, 'accounts/staff_list.html', {'staff_profiles': staff_profiles})

@login_required
def staff_create(request):
    from billing.utils import check_user_limit
    from django.contrib import messages
    import secrets
    
    try:
        profile = request.user.profile
        if profile.role != 'admin':
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        return redirect('landing')

    # Check user limit
    can_create, current_count, max_allowed = check_user_limit(profile.tenant)
    if not can_create:
        messages.error(request, f'User limit reached! Your plan allows {max_allowed} user(s). Upgrade to add more.')
        return redirect('staff_list')

    if request.method == 'POST':
        form = StaffCreationForm(request.POST, tenant=profile.tenant)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    
                    # Generate random 6-digit PIN
                    generated_pin = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
                    
                    # Log for testing (visible in terminal)
                    print(f"--- GENERATED STAFF PIN: {generated_pin} for {user.username} ---")
                    
                    # Create Profile - Explicitly avoiding any form.cleaned_data['pin'] access
                    UserProfile.objects.create(
                        user=user,
                        tenant=profile.tenant,
                        branch=form.cleaned_data['branch'],
                        role=form.cleaned_data['role'],
                        can_perform_credit_sales=form.cleaned_data.get('can_perform_credit_sales', False),
                        pos_pin=generated_pin
                    )

                    # Send Welcome Email
                    if user.email:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(f"Attempting to send welcome email to {user.email}...")
                        
                        try:
                            token = default_token_generator.make_token(user)
                            uid = urlsafe_base64_encode(force_bytes(user.pk))
                            reset_link = request.build_absolute_uri(
                                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                            )

                            html_message = render_to_string('emails/staff_welcome_pin.html', {
                                'user': user,
                                'tenant_name': profile.tenant.name,
                                'pin': generated_pin,
                                'reset_link': reset_link,
                            })
                            plain_message = strip_tags(html_message)

                            sent_count = send_mail(
                                subject=f"Welcome to {profile.tenant.name} - Your Staff Credentials",
                                message=plain_message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[user.email],
                                html_message=html_message,
                                fail_silently=False
                            )
                            logger.info(f"send_mail result: {sent_count}")
                            
                            if sent_count:
                                messages.success(request, f"Staff created and welcome email sent to {user.email}")
                            else:
                                logger.warning(f"Email to {user.email} was not sent (count=0).")
                                messages.warning(request, f"Staff created but email sending returned 0.")
                        except Exception as mail_e:
                            logger.error(f"Failed to send email to {user.email}: {str(mail_e)}", exc_info=True)
                            messages.warning(request, f"Staff created but welcome email failed: {str(mail_e)}")
                    else:
                        messages.success(request, f"Staff created. No email address provided to send credentials.")
                    
                    return redirect('staff_list')
            except Exception as e:
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Staff creation error: {str(e)}", exc_info=True)
                messages.error(request, f"Error creating staff: {str(e)}")
    else:
        form = StaffCreationForm(tenant=profile.tenant)
    
    return render(request, 'accounts/staff_form.html', {'form': form, 'title': 'Add New Staff'})

@login_required
def staff_update(request, pk):
    try:
        profile = request.user.profile
        if profile.role != 'admin':
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        return redirect('landing')

    staff_profile = get_object_or_404(UserProfile, pk=pk, tenant=profile.tenant)
    staff_user = staff_profile.user
    
    if request.method == 'POST':
        form = StaffUpdateForm(request.POST, instance=staff_user, tenant=profile.tenant)
        if form.is_valid():
            form.save()
            # Update Profile
            staff_profile.branch = form.cleaned_data['branch']
            staff_profile.role = form.cleaned_data['role']
            staff_profile.can_perform_credit_sales = form.cleaned_data.get('can_perform_credit_sales', False)
            staff_profile.save()
            
            from django.contrib import messages
            messages.success(request, f"Staff profile for {staff_user.username} updated successfully.")
            return redirect('staff_list')
    else:
        # Initial data for the form
        initial_data = {
            'role': staff_profile.role,
            'branch': staff_profile.branch,
            'can_perform_credit_sales': staff_profile.can_perform_credit_sales,
        }
        form = StaffUpdateForm(instance=staff_user, tenant=profile.tenant, initial=initial_data)
    
    return render(request, 'accounts/staff_form.html', {
        'form': form, 
        'title': f'Edit Staff: {staff_user.username}',
        'is_update': True
    })

@login_required
def staff_delete(request, pk):
    try:
        profile = request.user.profile
        if profile.role != 'admin':
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        return redirect('landing')

def verification_sent(request):
    """Render page telling user to check their email"""
    return render(request, 'accounts/verification_sent.html')

def activate_account(request, uidb64, token):
    """
    Activate user account if token is valid.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Valid token
        user.is_active = True
        user.save()
        
        # Mark profile as verified
        try:
            profile = user.profiles.first() # Getting by related_name
            if profile:
                profile.is_email_verified = True
                profile.save()
        except:
            pass
            
        # Login the user
        login(request, user)
        
        # Return success page or redirect
        return render(request, 'accounts/verification_success.html')
    else:
        return render(request, 'accounts/verification_failed.html')

        
    staff_profile = get_object_or_404(UserProfile, pk=pk, tenant=profile.tenant)
    if request.method == 'POST':
        staff_profile.user.delete() # Cascade deletes profile
        return redirect('staff_list')
    return render(request, 'accounts/staff_confirm_delete.html', {'staff': staff_profile})

@login_required
def user_profile(request):
    """
    Render the user's profile page.
    """
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return redirect('logout')
        
    branch_id = request.GET.get('branch_id')
    branch = None
    
    if branch_id:
        branch = get_object_or_404(Branch, id=branch_id, tenant=profile.tenant)
    elif profile.branch:
        branch = profile.branch
        
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'branch': branch,
    })

def logout_view(request):
    """
    Custom logout view to handle GET requests (Django 5+ default LogoutView requires POST)
    """
    from django.contrib.auth import logout
    if request.user.is_authenticated:
        logout(request)
    return redirect('landing')
