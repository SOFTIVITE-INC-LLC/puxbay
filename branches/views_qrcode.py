from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import Branch
import qrcode
import io
import base64

@login_required
def print_qr_code(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    tenant = branch.tenant
    
    # Construct Storefront URL
    # Assuming the URL pattern is /store/<tenant_slug>/<branch_id>/
    # We use build_absolute_uri to get the full domain
    store_path = f"/store/{tenant.subdomain}/{branch.id}/"
    full_url = request.build_absolute_uri(store_path)
    
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(full_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to Base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    # Generate Kiosk QR Code
    kiosk_path = f"/kiosk/{branch.id}/"
    kiosk_full_url = request.build_absolute_uri(kiosk_path)
    
    qr_kiosk = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr_kiosk.add_data(kiosk_full_url)
    qr_kiosk.make(fit=True)
    
    img_kiosk = qr_kiosk.make_image(fill_color="black", back_color="white")
    
    buffer_kiosk = io.BytesIO()
    img_kiosk.save(buffer_kiosk, format="PNG")
    img_kiosk_str = base64.b64encode(buffer_kiosk.getvalue()).decode()
    
    context = {
        'branch': branch,
        'tenant': tenant,
        'qr_code_base64': img_str,
        'store_url': full_url,
        'kiosk_qr_code_base64': img_kiosk_str,
        'kiosk_url': kiosk_full_url
    }
    return render(request, 'branches/print_qrcode.html', context)
