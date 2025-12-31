from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

from .models import StocktakeSession, StocktakeEntry, Branch, Product

def stocktake_portal_login(request, token):
    """
    Renders the public stocktake portal for a valid session token.
    Does not require user authentication.
    """
    session = get_object_or_404(StocktakeSession, access_token=token)
    
    if session.status == 'completed':
        return render(request, 'branches/stocktake/portal_closed.html', {'session': session})

    # Simple context for the Single Page App (SPA) feel
    context = {
        'session': session,
        'branch': session.branch,
        'token': token,
    }
    return render(request, 'branches/stocktake/portal_app.html', context)

def stocktake_api_scan(request, token):
    """
    API to lookup a product by barcode/SKU within the branch.
    """
    session = get_object_or_404(StocktakeSession, access_token=token)
    if session.status == 'completed':
        return JsonResponse({'error': 'Session closed'}, status=403)

    query = request.GET.get('q', '').strip()
    
    if not query:
        # Return all entries in session (limit 50)
        # Prioritize uncounted or just alphabetical
        entries = StocktakeEntry.objects.filter(session=session).select_related('product').order_by('product__name')[:100]
        results = []
        for entry in entries:
             results.append({
                'id': entry.product.id,
                'name': entry.product.name,
                'barcode': entry.product.barcode,
                'sku': entry.product.sku,
                'current_count': entry.counted_quantity,
                'image_url': entry.product.image.url if entry.product.image else None,
            })
        return JsonResponse({'results': results})

    # Search by barcode or name
    products = Product.objects.filter(
        branch=session.branch,
        is_active=True
    ).filter(
        Q(barcode=query) | Q(name__icontains=query) | Q(sku__iexact=query)
    )[:20]

    results = []
    for p in products:
        # Get existing entry if any
        entry = StocktakeEntry.objects.filter(session=session, product=p).first()
        current_count = entry.counted_quantity if entry else 0
        
        results.append({
            'id': p.id,
            'name': p.name,
            'barcode': p.barcode,
            'sku': p.sku,
            'current_count': current_count,
            'image_url': p.image.url if p.image else None,
        })

    return JsonResponse({'results': results})

@csrf_exempt # Using token for auth, but ideally should use CSRF. For simplicity in this specific ephemeral portal flow.
@require_POST
def stocktake_api_update(request, token):
    """
    API to update the count for a product.
    """
    session = get_object_or_404(StocktakeSession, access_token=token)
    if session.status == 'completed':
        return JsonResponse({'error': 'Session closed'}, status=403)

    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 0))
        mode = data.get('mode', 'set') # 'set' or 'add'
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid data'}, status=400)

    product = get_object_or_404(Product, pk=product_id, branch=session.branch)

    # Get or Create Entry
    entry, created = StocktakeEntry.objects.get_or_create(
        session=session,
        product=product,
        defaults={'expected_quantity': product.stock_quantity}
    )

    if mode == 'add':
        entry.counted_quantity += quantity
    else:
        entry.counted_quantity = quantity
    
    entry.save()

    return JsonResponse({
        'success': True,
        'product_id': product.id,
        'new_count': entry.counted_quantity
    })
