from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Shift, Branch
from .forms import ShiftAssignmentForm
from accounts.models import UserProfile
from .services.staff import StaffService
from datetime import datetime, timedelta

@login_required
def shift_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    shifts = Shift.objects.filter(branch=branch).order_by('start_time')
    
    # Filter by date if provided
    date_str = request.GET.get('date')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            shifts = shifts.filter(start_time__date=target_date)
        except ValueError:
            pass
            
    today_str = timezone.now().strftime('%Y-%m-%d')
            
    return render(request, 'branches/shifts/shift_list.html', {
        'branch': branch,
        'shifts': shifts,
        'today_str': today_str,
    })

@login_required
def schedule_shift(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    staff_service = StaffService(tenant=request.user.profile.tenant)
    
    if request.method == 'POST':
        form = ShiftAssignmentForm(request.POST, tenant=request.user.profile.tenant)
        if form.is_valid():
            shift_data = form.cleaned_data
            
            result = staff_service.schedule_shift(
                staff_id=shift_data['staff'].id,
                branch_id=branch_id,
                start_time=shift_data['start_time'],
                end_time=shift_data['end_time'],
                role=shift_data['role'],
                notes=shift_data['notes']
            )
            
            if result['status'] == 'success':
                messages.success(request, "Shift scheduled successfully.")
                return redirect('shift_list', branch_id=branch_id)
            else:
                messages.error(request, f"Error: {result['message']}")
    else:
        form = ShiftAssignmentForm(tenant=request.user.profile.tenant)
        # Default start time to tomorrow 8 AM
        tomorrow = timezone.now().date() + timedelta(days=1)
        start_default = timezone.make_aware(datetime.combine(tomorrow, datetime.min.time().replace(hour=8)))
        form.fields['start_time'].initial = start_default
        form.fields['end_time'].initial = start_default + timedelta(hours=8)
            
    return render(request, 'branches/shifts/shift_form.html', {
        'branch': branch,
        'form': form,
    })

@login_required
def shift_check_in(request, shift_id):
    staff_service = StaffService(tenant=request.user.profile.tenant)
    result = staff_service.check_in(shift_id)
    
    if result['status'] == 'success':
        messages.success(request, "Checked in successfully.")
    else:
        messages.error(request, f"Error: {result['message']}")
        
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def shift_check_out(request, shift_id):
    staff_service = StaffService(tenant=request.user.profile.tenant)
    result = staff_service.check_out(shift_id)
    
    if result['status'] == 'success':
        messages.success(request, "Checked out successfully.")
    else:
        messages.error(request, f"Error: {result['message']}")
        
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def staff_performance_report(request, branch_id, staff_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    staff = get_object_or_404(UserProfile, pk=staff_id, tenant=request.user.profile.tenant)
    staff_service = StaffService(tenant=request.user.profile.tenant)
    
    # Date range (default last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    start_str = request.GET.get('start_date')
    end_str = request.GET.get('end_date')
    
    if start_str and end_str:
        try:
            start_date = timezone.make_aware(datetime.strptime(start_str, '%Y-%m-%d'))
            end_date = timezone.make_aware(datetime.strptime(end_str, '%Y-%m-%d'))
        except ValueError:
            pass
            
    result = staff_service.get_staff_performance(staff_id, start_date, end_date)
    
    return render(request, 'branches/shifts/performance_report.html', {
        'branch': branch,
        'staff': staff,
        'performance': result.get('metrics') if result['status'] == 'success' else None,
        'start_date': start_date,
        'end_date': end_date,
    })
