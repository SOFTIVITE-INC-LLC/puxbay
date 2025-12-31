from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import Attendance
from main.models import MarketingCampaign, CustomerFeedback

from branches.forms_marketing import MarketingCampaignForm
from django.contrib import messages

@login_required
def company_marketing_list(request):
    """Company-wide marketing campaigns"""
    if request.user.profile.role not in ['admin', 'manager']:
         return redirect('dashboard')
         
    campaigns = MarketingCampaign.objects.filter(tenant=request.user.profile.tenant).order_by('-created_at')
    
    return render(request, 'branches/campaign_list.html', {
        'campaigns': campaigns,
        'is_company_view': True,
        'title': 'Marketing Campaigns'
    })

@login_required
def company_campaign_create(request):
    """Create a company-wide marketing campaign"""
    if request.user.profile.role not in ['admin', 'manager']:
         return redirect('dashboard')

    if request.method == 'POST':
        form = MarketingCampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.tenant = request.user.profile.tenant
            campaign.status = 'draft' # Always start as draft
            campaign.save()
            messages.success(request, 'Campaign draft created.')
            return redirect('company_marketing_list')
    else:
        form = MarketingCampaignForm()
        
    return render(request, 'branches/crm/campaign_form.html', {
        'form': form,
        'title': 'Create Campaign',
        'is_company_view': True
    })

@login_required
def company_feedback_list(request):
    """Company-wide customer feedback"""
    if request.user.profile.role not in ['admin', 'manager']:
         return redirect('dashboard')

    feedback_list = CustomerFeedback.objects.filter(tenant=request.user.profile.tenant).select_related('customer', 'transaction', 'transaction__branch').order_by('-created_at')
    
    return render(request, 'branches/feedback_list.html', {
        'feedback_list': feedback_list,
        'is_company_view': True,
        'title': 'Customer Feedback'
    })

@login_required
def company_attendance_list(request):
    """Company-wide attendance records"""
    if request.user.profile.role not in ['admin', 'manager']:
         return redirect('dashboard')

    attendance_records = Attendance.objects.filter(user__tenant=request.user.profile.tenant).select_related('user', 'user__user', 'branch').order_by('-clock_in')
    
    return render(request, 'branches/attendance_list.html', {
        'attendance_records': attendance_records,
        'is_company_view': True, # Use this in template to hide "Clock In/Out" buttons or adjust layout
        'title': 'Staff Attendance'
    })
