from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Branch
from branches.models import Shift
from branches.models_workforce import ShiftSwapRequest
from branches.services.gamification_service import GamificationService

@login_required
def staff_portal_view(request, branch_id):
    """Main portal for staff members to see their stats and schedule"""
    tenant = request.user.profile.tenant
    branch = get_object_or_404(Branch, id=branch_id, tenant=tenant)
    staff_profile = request.user.profile

    service = GamificationService(tenant=tenant)
    
    # Evaluate for new achievements on view
    service.evaluate_achievements(staff_profile)
    
    # Get commissions and achievements
    commission_data = service.calculate_commissions(staff_profile)
    achievements = staff_profile.achievements.all().order_by('-earned_at')
    
    # Get upcoming shifts and pending swaps
    upcoming_shifts = Shift.objects.filter(
        staff=staff_profile,
        start_time__date__gte=datetime.date.today(),
        branch=branch
    ).order_by('start_time')
    
    open_shifts = Shift.objects.filter(
        branch=branch,
        is_for_bid=True,
        staff__isnull=True,
        start_time__date__gte=datetime.date.today()
    )
    
    pending_swaps = ShiftSwapRequest.objects.filter(
        target_staff=staff_profile,
        status='pending'
    )

    context = {
        'branch': branch,
        'commission_data': commission_data,
        'achievements': achievements,
        'upcoming_shifts': upcoming_shifts,
        'open_shifts': open_shifts,
        'pending_swaps': pending_swaps
    }
    return render(request, 'branches/workforce/staff_portal.html', context)

import datetime

@login_required
def request_shift_swap(request, branch_id, shift_id):
    """Allows staff to request a swap for a shift"""
    tenant = request.user.profile.tenant
    shift = get_object_or_404(Shift, id=shift_id, staff=request.user.profile, branch__tenant=tenant)
    
    if request.method == 'POST':
        target_staff_id = request.POST.get('target_staff')
        notes = request.POST.get('notes', '')
        
        # In a real app, we'd list other staff members in the template
        # For now, we'll just handle the creation if target_staff_id is provided
        # or mark it for general bidding if target is null
        
        swap_req = ShiftSwapRequest.objects.create(
            requesting_staff=request.user.profile,
            original_shift=shift,
            notes=notes
        )
        
        shift.is_for_bid = True
        shift.save()
        
        messages.success(request, "Shift swap request sent!")
        return redirect('staff_portal', branch_id=branch_id)
        
    return render(request, 'branches/workforce/swap_request_form.html', {'shift': shift, 'branch_id': branch_id})

@login_required
def claim_open_shift(request, branch_id, shift_id):
    """Allows staff to bid on and claim an open shift"""
    tenant = request.user.profile.tenant
    shift = get_object_or_404(Shift, id=shift_id, is_for_bid=True, branch__tenant=tenant)
    
    shift.staff = request.user.profile
    shift.is_for_bid = False
    shift.save()
    
    messages.success(request, f"You have claimed the shift for {shift.start_time.strftime('%b %d, %H:%M')}")
    return redirect('staff_portal', branch_id=branch_id)
