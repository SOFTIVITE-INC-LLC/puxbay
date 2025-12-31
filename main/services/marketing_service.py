from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from ..models import MarketingCampaign, Customer, CustomerTier
import logging

logger = logging.getLogger(__name__)

def process_scheduled_campaigns():
    """Finds and sends scheduled manual campaigns that have reached their target time."""
    now = timezone.now()
    pending = MarketingCampaign.objects.filter(
        status='scheduled',
        scheduled_at__lte=now,
        is_automated=False
    )
    
    for campaign in pending:
        send_campaign_to_targets(campaign)
        campaign.status = 'sent'
        campaign.sent_at = now
        campaign.save()

def trigger_automated_campaigns(event_type, customer):
    """Triggers workflows based on specific events like 'first_purchase' or 'tier_up'."""
    campaigns = MarketingCampaign.objects.filter(
        tenant=customer.tenant,
        is_automated=True,
        trigger_event=event_type,
        status='scheduled' # Using 'scheduled' as 'active' for automated ones
    )
    
    for campaign in campaigns:
        # Check tier restriction
        if campaign.target_tier and customer.tier != campaign.target_tier:
            continue
            
        send_campaign_notification(campaign, customer)

def check_periodic_triggers():
    """Daily checks for 'birthday' and 'inactive_30d' triggers."""
    now = timezone.now()
    today = now.date()
    
    # 1. Birthday triggers
    birthday_campaigns = MarketingCampaign.objects.filter(
        is_automated=True,
        trigger_event='birthday',
        status='scheduled'
    )
    
    for campaign in birthday_campaigns:
        # Customers with birthday today (matching month and day)
        targets = Customer.objects.filter(
            tenant=campaign.tenant,
            birth_date__month=today.month,
            birth_date__day=today.day,
            marketing_opt_in=True
        )
        for customer in targets:
            send_campaign_notification(campaign, customer)
        
        campaign.last_run_at = now
        campaign.save()

    # 2. Inactive triggers (30 days)
    inactive_date = now - timedelta(days=30)
    inactive_campaigns = MarketingCampaign.objects.filter(
        is_automated=True,
        trigger_event='inactive_30d',
        status='scheduled'
    )
    
    for campaign in inactive_campaigns:
        # Customers whose last purchase was EXACTLY 30 days ago (or within a window)
        # To avoid double sending, we might want to track if they've received this campaign before
        targets = Customer.objects.filter(
            tenant=campaign.tenant,
            last_purchase_at__date=inactive_date.date(),
            marketing_opt_in=True
        )
        for customer in targets:
            send_campaign_notification(campaign, customer)
            
        campaign.last_run_at = now
        campaign.save()

def send_campaign_to_targets(campaign):
    """Helper to send a manual campaign to its intended audience."""
    targets = Customer.objects.filter(
        tenant=campaign.tenant,
        marketing_opt_in=True
    )
    
    if campaign.target_tier:
        targets = targets.filter(tier=campaign.target_tier)
        
    for customer in targets:
        send_campaign_notification(campaign, customer)

def send_campaign_notification(campaign, customer):
    """The final delivery step (Email/SMS) using branded templates."""
    if campaign.campaign_type == 'email' and customer.email:
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.conf import settings
        
        # Get tenant for branding
        tenant = campaign.tenant
        
        # Build context
        context = {
            'campaign': campaign,
            'customer': customer,
            'tenant': tenant,
        }
        
        # Render HTML
        html_message = render_to_string('emails/campaign_branded.html', context)
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=campaign.subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[customer.email],
                html_message=html_message,
                fail_silently=False
            )
            logger.info(f"Sent branded email campaign '{campaign.name}' to {customer.email}")
        except Exception as e:
            logger.error(f"Failed to send campaign email to {customer.email}: {e}")
            
    elif campaign.campaign_type == 'sms':
        # Placeholder for SMS delivery
        logger.info(f"Sending SMS campaign '{campaign.name}' to {customer.phone}")
