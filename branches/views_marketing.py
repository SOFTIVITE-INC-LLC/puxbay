from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.models import Branch
from main.models import MarketingCampaign, Customer
from .forms_marketing import MarketingCampaignForm

@login_required
def campaign_list(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    # Permission check
    if request.user.profile.role not in ['admin', 'manager']:
        return redirect('branch_dashboard', branch_id=branch.id)
        
    campaigns = MarketingCampaign.objects.filter(tenant=request.user.profile.tenant).order_by('-created_at')
    
    context = {
        'branch': branch,
        'campaigns': campaigns,
        'title': 'Marketing Campaigns'
    }
    return render(request, 'branches/crm/campaign_list.html', context)

@login_required
def campaign_create(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    
    if request.method == 'POST':
        form = MarketingCampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.tenant = request.user.profile.tenant
            campaign.status = 'draft' # Always start as draft
            campaign.save()
            messages.success(request, 'Campaign draft created.')
            return redirect('campaign_list', branch_id=branch.id)
    else:
        form = MarketingCampaignForm()
        
    context = {
        'branch': branch,
        'form': form,
        'title': 'Create Campaign'
    }
    return render(request, 'branches/crm/campaign_form.html', context)

@login_required
def campaign_update(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    campaign = get_object_or_404(MarketingCampaign, pk=pk, tenant=request.user.profile.tenant)
    
    if campaign.status == 'sent':
        messages.error(request, 'Cannot edit a sent campaign.')
        return redirect('campaign_list', branch_id=branch.id)
    
    if request.method == 'POST':
        form = MarketingCampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaign updated.')
            return redirect('campaign_list', branch_id=branch.id)
    else:
        form = MarketingCampaignForm(instance=campaign)
        
    context = {
        'branch': branch,
        'form': form,
        'title': 'Edit Campaign'
    }
    return render(request, 'branches/crm/campaign_form.html', context)

@login_required
def campaign_delete(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    campaign = get_object_or_404(MarketingCampaign, pk=pk, tenant=request.user.profile.tenant)
    
    if request.method == 'POST':
        campaign.delete()
        messages.success(request, 'Campaign deleted.')
        return redirect('campaign_list', branch_id=branch.id)
        
    return redirect('campaign_list', branch_id=branch.id)

@login_required
def campaign_send(request, branch_id, pk):
    branch = get_object_or_404(Branch, pk=branch_id, tenant=request.user.profile.tenant)
    campaign = get_object_or_404(MarketingCampaign, pk=pk, tenant=request.user.profile.tenant)
    
    if campaign.status == 'sent':
        messages.warning(request, 'Campaign already sent.')
        return redirect('campaign_list', branch_id=branch.id)
        
    if request.method == 'POST':
        # Identify recipients
        if campaign.target_tier:
            recipients = Customer.objects.filter(tenant=branch.tenant, tier=campaign.target_tier, marketing_opt_in=True)
        else:
            recipients = Customer.objects.filter(tenant=branch.tenant, marketing_opt_in=True)
            
        count = recipients.count()
        
        if count == 0:
            messages.warning(request, 'No eligible recipients found for this campaign.')
            return redirect('campaign_list', branch_id=branch.id)
        
        # Send emails
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.conf import settings as django_settings
        import re
        
        sent_count = 0
        failed_count = 0
        
        # Extract email from DEFAULT_FROM_EMAIL
        from_email_raw = django_settings.DEFAULT_FROM_EMAIL
        email_match = re.search(r'<(.+?)>', from_email_raw)
        if email_match:
            from_email = email_match.group(1)
        else:
            from_email = from_email_raw
        
        formatted_from = f"{branch.tenant.name} <{from_email}>"
        
        for customer in recipients:
            if not customer.email:
                continue
                
            try:
                # Prepare context for template
                context = {
                    'campaign': campaign,
                    'customer': customer,
                    'tenant_name': branch.tenant.name,
                    'tier_info': customer.tier,
                    'loyalty_points': customer.loyalty_points if customer.loyalty_points > 0 else None,
                    'cta_url': f"http://{branch.tenant.subdomain}.localhost:8000/store/{branch.tenant.subdomain}/{branch.id}/",
                    'cta_text': 'Visit Our Store',
                    'unsubscribe_url': None,  # TODO: Implement unsubscribe functionality
                }
                
                # Render email template
                html_message = render_to_string('emails/marketing_campaign.html', context)
                plain_message = strip_tags(html_message)
                
                # Create email
                email = EmailMultiAlternatives(
                    subject=campaign.subject or campaign.name,
                    body=plain_message,
                    from_email=formatted_from,
                    to=[customer.email],
                    reply_to=[from_email],
                )
                
                # Attach HTML version
                email.attach_alternative(html_message, "text/html")
                
                # Add headers for better deliverability
                email.extra_headers = {
                    'X-Campaign-ID': str(campaign.id),
                    'X-Mailer': 'Django',
                    'Message-ID': f"<campaign-{campaign.id}-{customer.id}@{branch.tenant.subdomain}.pos>",
                    'List-Unsubscribe': f'<mailto:{from_email}?subject=Unsubscribe>',
                    'Precedence': 'bulk',
                    'X-Auto-Response-Suppress': 'OOF, AutoReply',
                }
                
                # Send email
                email.send(fail_silently=False)
                sent_count += 1
                
                print(f"[Marketing] Sent campaign '{campaign.name}' to {customer.email}")
                
            except Exception as e:
                failed_count += 1
                print(f"[Marketing Error] Failed to send to {customer.email}: {e}")
                import traceback
                traceback.print_exc()
        
        # Update campaign status
        campaign.status = 'sent'
        campaign.sent_at = timezone.now()
        campaign.save()
        
        if failed_count > 0:
            messages.warning(request, f'Campaign "{campaign.name}" sent to {sent_count} customers. {failed_count} failed.')
        else:
            messages.success(request, f'Campaign "{campaign.name}" successfully sent to {sent_count} customers!')
            
        return redirect('campaign_list', branch_id=branch.id)
    
    context = {
        'branch': branch,
        'campaign': campaign,
        'recipient_count': Customer.objects.filter(tenant=branch.tenant, tier=campaign.target_tier, marketing_opt_in=True).count() if campaign.target_tier else Customer.objects.filter(tenant=branch.tenant, marketing_opt_in=True).count(),
        'title': 'Send Campaign'
    }
    return render(request, 'branches/crm/campaign_confirm_send.html', context)

