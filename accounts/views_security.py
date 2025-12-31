import pyotp
import qrcode
import io
import base64
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import OTPVerificationForm
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

@login_required
def setup_2fa(request):
    profile = request.user.profile
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']
            secret = form.cleaned_data['secret']
            
            totp = pyotp.TOTP(secret)
            if totp.verify(otp_code):
                profile.otp_secret = secret
                profile.is_2fa_enabled = True
                profile.save()
                
                request.session['is_2fa_verified'] = True
                
                messages.success(request, "Two-Factor Authentication enabled successfully!")
                if profile.branch:
                    return redirect('branch_dashboard', branch_id=profile.branch.id)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid authentication code. Please try again.")
    else:
        # Generate new secret if one doesn't exist or if they are setting up again
        if not profile.otp_secret or not profile.is_2fa_enabled:
            secret = pyotp.random_base32()
        else:
            secret = profile.otp_secret 
        form = OTPVerificationForm(initial={'secret': secret})

    # Generate QR Code
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=request.user.email,
        issuer_name=request.user.profile.tenant.name
    )
    
    qr = qrcode.make(provisioning_uri)
    img_buffer = io.BytesIO()
    qr.save(img_buffer, format="PNG")
    qr_image_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    context = {
        'secret': secret,
        'qr_image': qr_image_base64,
        'is_enabled': profile.is_2fa_enabled,
        'branch': profile.branch,
        'form': form,
    }
    return render(request, 'accounts/security/2fa_setup.html', context)

@login_required
def verify_2fa(request):
    if request.session.get('is_2fa_verified'):
        profile = request.user.profile
        if profile.branch:
            return redirect('branch_dashboard', branch_id=profile.branch.id)
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']
            profile = request.user.profile
            
            if not profile.otp_secret:
                return redirect('setup_2fa')
                
            totp = pyotp.TOTP(profile.otp_secret)
            if totp.verify(otp_code):
                request.session['is_2fa_verified'] = True
                
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                
                if profile.branch:
                    return redirect('branch_dashboard', branch_id=profile.branch.id)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid code.")
    else:
        form = OTPVerificationForm()
            
    return render(request, 'accounts/security/2fa_verify.html', {'form': form})

@login_required
def disable_2fa(request):
    if request.method == 'POST':
        profile = request.user.profile
        profile.is_2fa_enabled = False
        profile.otp_secret = None
        profile.save()
        request.session.pop('is_2fa_verified', None)
        messages.success(request, "Two-Factor Authentication has been disabled.")
        return redirect('setup_2fa')
    return redirect('setup_2fa')
