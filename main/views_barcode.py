"""
Barcode views for generating and displaying barcodes.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from main.models import Product
from accounts.models import Branch
from main.services.barcode_service import (
    create_product_barcode,
    generate_barcode_image,
    get_barcode_svg,
    bulk_generate_barcodes
)
from django.contrib import messages
from django.shortcuts import redirect


@login_required
def generate_product_barcode(request, branch_id, product_id):
    """Generate barcode for a single product."""
    product = get_object_or_404(Product, id=product_id, branch_id=branch_id, tenant=request.user.profile.tenant)
    
    create_product_barcode(product, save=True)
    messages.success(request, f"Barcode generated for {product.name}")
    
    # Redirect back to the product detail page with branch context
    return redirect('product_detail', branch_id=branch_id, pk=product.id)


@login_required
def barcode_image(request, product_id, format='png'):
    """Return barcode image for a product."""
    product = get_object_or_404(Product, id=product_id, tenant=request.user.profile.tenant)
    
    if not product.barcode:
        create_product_barcode(product, save=True)
    
    if format == 'svg':
        svg_content = get_barcode_svg(product.barcode)
        if svg_content:
            return HttpResponse(svg_content, content_type='image/svg+xml')
    else:
        image_buffer = generate_barcode_image(product.barcode)
        if image_buffer:
            return HttpResponse(image_buffer.getvalue(), content_type='image/png')
    
    return HttpResponse("Error generating barcode", status=500)


@login_required
def print_barcode_label(request, product_id):
    """Render printable barcode label."""
    product = get_object_or_404(Product, id=product_id, tenant=request.user.profile.tenant)
    
    if not product.barcode:
        create_product_barcode(product, save=True)
    
    from django.shortcuts import render
    return render(request, 'main/barcode_label.html', {
        'product': product,
    })


@login_required
def bulk_generate_barcodes_view(request, branch_id):
    """Generate barcodes for all products without barcodes in a specific branch."""
    tenant = request.user.profile.tenant
    branch = get_object_or_404(Branch, id=branch_id, tenant=tenant)
    
    products = Product.objects.filter(
        tenant=tenant,
        branch=branch,
        barcode__isnull=True
    ) | Product.objects.filter(
        tenant=tenant,
        branch=branch,
        barcode=''
    )
    
    result = bulk_generate_barcodes(products)
    
    messages.success(
        request,
        f"Generated {result['success']} barcodes out of {result['total']} products"
    )
    
    if result['errors']:
        for error in result['errors'][:5]:  # Show first 5 errors
            messages.warning(request, f"{error['product']}: {error['error']}")
    
    # Redirect back to the branch dashboard
    return redirect('branch_dashboard', branch_id=branch.id)
