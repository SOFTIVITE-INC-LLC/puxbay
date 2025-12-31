from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Branch, StocktakeSession, StocktakeEntry, Product, StockMovement
from accounts.models import UserProfile

@login_required
def stocktake_list(request, branch_id):
    try:
        profile = request.user.profile
        if profile.branch and str(profile.branch.id) != str(branch_id) and profile.role != 'admin':
             return redirect('branch_dashboard', branch_id=profile.branch.id)
    except UserProfile.DoesNotExist:
        return redirect('landing')

    branch = get_object_or_404(Branch, pk=branch_id)
    sessions = StocktakeSession.objects.filter(branch=branch).order_by('-started_at')

    return render(request, 'branches/stocktake/list.html', {
        'branch': branch,
        'sessions': sessions,
        'title': 'Stocktake Sessions'
    })

@login_required
def stocktake_start(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)
    
    # Check if there is already an in-progress session
    ongoing = StocktakeSession.objects.filter(branch=branch, status='in_progress').first()
    if ongoing:
        messages.warning(request, "There is already an in-progress stocktake session.")
        return redirect('stocktake_detail', branch_id=branch.id, session_id=ongoing.id)

    if request.method == 'POST':
        # Create new session
        session = StocktakeSession.objects.create(
            branch=branch,
            created_by=request.user.profile,
            notes=request.POST.get('notes', '')
        )
        
        # Pre-populate entries with all current products? 
        # Strategy: We can either pre-populate ALL products, or let them add as they scan.
        # Pre-populating is usually safer to ensure nothing is missed.
        products = Product.objects.filter(branch=branch, is_active=True)
        entries = []
        for p in products:
            entries.append(StocktakeEntry(
                session=session,
                product=p,
                counted_quantity=0, # User starts fresh
                expected_quantity=p.stock_quantity # Snapshot of current stock
            ))
        StocktakeEntry.objects.bulk_create(entries)
        
        return redirect('stocktake_detail', branch_id=branch.id, session_id=session.id)

    return redirect('stocktake_list', branch_id=branch.id)

@login_required
def stocktake_detail(request, branch_id, session_id):
    branch = get_object_or_404(Branch, pk=branch_id)
    session = get_object_or_404(StocktakeSession, pk=session_id, branch=branch)
    
    entries = session.entries.select_related('product').all().order_by('product__name')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_count':
            entry_id = request.POST.get('entry_id')
            new_count = request.POST.get('counted_quantity')
            entry = get_object_or_404(StocktakeEntry, pk=entry_id, session=session)
            try:
                entry.counted_quantity = int(new_count)
                entry.save()
            except (ValueError, TypeError):
                messages.error(request, "Invalid quantity.")

        elif action == 'adjust_single':
            entry_id = request.POST.get('entry_id')
            entry = get_object_or_404(StocktakeEntry, pk=entry_id, session=session)
            
            # Apply adjustment logic
            current_stock = entry.product.stock_quantity
            diff = entry.counted_quantity - current_stock
            
            if diff != 0:
                entry.product.stock_quantity = entry.counted_quantity
                entry.product.save()
                
                StockMovement.objects.create(
                    tenant=branch.tenant,
                    branch=branch,
                    product=entry.product,
                    quantity_change=diff,
                    balance_after=entry.counted_quantity,
                    movement_type='adjustment',
                    reference=f"ST-{session.id.hex[:8].upper()}",
                    notes=f"Single Adjustment: Counted {entry.counted_quantity}, was {current_stock}.",
                    created_by=request.user.profile
                )
                messages.success(request, f"Adjusted {entry.product.name} to {entry.counted_quantity}.")
            else:
                messages.info(request, f"{entry.product.name} stock level is already correct.")

        elif action == 'adjust_all':
            entries_to_adjust = session.entries.select_related('product').all()
            adjust_count = 0
            for entry in entries_to_adjust:
                current_stock = entry.product.stock_quantity
                diff = entry.counted_quantity - current_stock
                if diff != 0:
                    entry.product.stock_quantity = entry.counted_quantity
                    entry.product.save()
                    StockMovement.objects.create(
                        tenant=branch.tenant,
                        branch=branch,
                        product=entry.product,
                        quantity_change=diff,
                        balance_after=entry.counted_quantity,
                        movement_type='adjustment',
                        reference=f"ST-{session.id.hex[:8].upper()}",
                        notes=f"Bulk Adjustment (Internal): Counted {entry.counted_quantity}, was {current_stock}.",
                        created_by=request.user.profile
                    )
                    adjust_count += 1
            messages.success(request, f"Applied adjustments to {adjust_count} items. Session remains in progress.")

        elif action == 'finalize':
            return redirect('stocktake_finalize', branch_id=branch.id, session_id=session.id)

        return redirect('stocktake_detail', branch_id=branch.id, session_id=session.id)

    return render(request, 'branches/stocktake/detail.html', {
        'branch': branch,
        'session': session,
        'entries': entries,
        'title': f'Stocktake - {session.started_at.date()}'
    })

@login_required
@transaction.atomic
def stocktake_finalize(request, branch_id, session_id):
    branch = get_object_or_404(Branch, pk=branch_id)
    session = get_object_or_404(StocktakeSession, pk=session_id, branch=branch)

    if session.status == 'completed':
        messages.warning(request, "Session already completed.")
        return redirect('stocktake_detail', branch_id=branch.id, session_id=session.id)

    if request.method == 'POST':
        # Removed auto-adjustment logic from finalization.
        # Adjustments should now be performed manually via 'Adjust' or 'Adjust All' buttons.
        
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.save()
        messages.success(request, "Stocktake session finalized. No automatic stock adjustments were performed.")
        return redirect('stocktake_list', branch_id=branch.id)

    return render(request, 'branches/stocktake/finalize_confirm.html', {
        'branch': branch,
        'session': session,
        'title': 'Finalize Stocktake'
    })
@login_required
def stocktake_analytics(request, branch_id, session_id):
    from django.db.models import Sum, F, Count, Q
    branch = get_object_or_404(Branch, pk=branch_id)
    session = get_object_or_404(StocktakeSession, pk=session_id, branch=branch)
    
    entries = session.entries.all()
    total_items = entries.count()
    
    # KPIs
    perfect_matches = entries.filter(counted_quantity=F('expected_quantity')).count()
    discrepancies = total_items - perfect_matches
    accuracy_rate = (perfect_matches / total_items * 100) if total_items > 0 else 0
    
    # Financial Impact
    # Note: We use expected_quantity * cost_price vs counted_quantity * cost_price
    stats = entries.annotate(
        diff=F('counted_quantity') - F('expected_quantity'),
        diff_val=F('counted_quantity') * F('product__cost_price') - F('expected_quantity') * F('product__cost_price')
    ).aggregate(
        total_loss=Sum('diff_val', filter=Q(diff__lt=0)),
        total_gain=Sum('diff_val', filter=Q(diff__gt=0)),
        net_impact=Sum('diff_val')
    )

    # Top discrepancies (by absolute value)
    top_discrepancies = entries.annotate(
        abs_diff=F('counted_quantity') - F('expected_quantity')
    ).order_by('abs_diff')[:10] # Showing top losses usually

    return render(request, 'branches/stocktake/analytics.html', {
        'branch': branch,
        'session': session,
        'perfect_matches': perfect_matches,
        'discrepancies': discrepancies,
        'accuracy_rate': accuracy_rate,
        'stats': stats,
        'top_discrepancies': top_discrepancies,
        'title': 'Stocktake Analytics'
    })
