from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Notification, NotificationSetting
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_notification(user, title, message, level='info', category='general', link=None):
    """
    Creates a Notification object and optionally sends an email if enabled.
    Also triggers a real-time WebSocket notification.
    """
    # Create in-app notification
    Notification.objects.create(
        recipient=user,
        title=title,
        message=message,
        notification_type=level,
        category=category,
        link=link
    )

    # Trigger WebSocket notification
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{user.id}",
                {
                    "type": "send_notification",
                    "message": {
                        "title": title,
                        "body": message,
                        "level": level,
                        "category": category,
                        "link": link
                    }
                }
            )
    except Exception as e:
        print(f"[WS Error] Failed to send real-time notification: {e}")
    
    # Check preferences for email
    try:
        settings_obj = user.notification_settings
        if not settings_obj.email_notifications:
            return
            
        should_send = False
        if category == 'inventory' and settings_obj.low_stock_alerts:
            should_send = True
        elif category == 'sales' and settings_obj.sales_reports:
            should_send = True
        elif category == 'security' and settings_obj.security_alerts:
            should_send = True
        elif category == 'system' and settings_obj.system_alerts:
            should_send = True
        elif category == 'general':
            should_send = True
            
        if should_send and user.email:
            # Generate HTML content
            # Try to find a specific template for the category, fallback to generic notification
            template_name = f'emails/{category}_notification_email.html'
            # Check if template exists logic could be here, but for now we'll use a mapping or just the specific order one we made
            # Actually, let's use the generic 'notification_email.html' if we haven't made specific ones for every category,
            # OR just use 'order_notification_email.html' for sales/orders.

            # For simplicity in this 'Branded System' task, we will use the order template for 'sales' 
            # and a generic one for others, or just use one template dynamically.
            # Let's map 'sales' to 'order_notification_email.html' and others to 'notification_email.html' (which we can alias or create)
            
            # Since we just created 'order_notification_email.html', let's use it for checks. 
            # Ideally we have a generic email. Let's assume order_notification_email.html acts as our generic 
            # "Actionable Notification" template since it takes title, message, link.
            
            email_context = {
                'user': user,
                'title': title,
                'message': message,
                'category': category,
                'link': link
            }
            
            html_message = render_to_string('emails/order_notification_email.html', email_context)
            plain_message = strip_tags(html_message)

            send_mail(
                subject=f"[{category.upper()}] {title}",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=True
            )
            
    except NotificationSetting.DoesNotExist:
        # For now, let's just create the in-app notification.
        pass
def trigger_new_order_notification(order):
    """
    Sends a notification to all users in the branch about a new online order.
    """
    from accounts.models import UserProfile
    from django.urls import reverse
    from django.db.models import Q
    
    # Get users assigned to this branch OR Admins of the tenant
    branch_users = UserProfile.objects.filter(
        tenant=order.tenant
    ).filter(
        Q(branch=order.branch) | Q(role='admin')
    ).select_related('user')
    
    # Generate link to the order details in admin or dashboard
    # Adjust 'admin:main_order_change' if you want them to go to the Django admin
    # Or a dashboard URL if available.
    try:
        # Try to link to the dashboard order detail view if possible, otherwise admin
        # Assuming there is a view 'transaction_detail' in branches app
        order_link = reverse('transaction_detail', kwargs={'branch_id': order.branch.id, 'order_id': order.id})
    except:
        try:
            order_link = reverse('admin:main_order_change', args=[order.id])
        except:
            order_link = None

    for profile in branch_users:
        if profile.user:
            send_notification(
                user=profile.user,
                title=f"New Order #{order.id} ({order.branch.name})",
                message=f"New online order from {order.customer.name} for ${order.total_amount}",
                level='success',
                category='sales',
                link=order_link
            )

def send_order_status_email_to_customer(order):
    """
    Sends an email to the customer when their order status changes.
    """
    print(f"[Email Debug] Attempting to send email for order {order.order_number}")
    
    if not order.customer:
        print(f"[Email Debug] No customer associated with order {order.order_number}")
        return
    
    if not order.customer.email:
        print(f"[Email Debug] Customer {order.customer.name} has no email address")
        return

    status_messages = {
        'pending': 'We have received your order and it is pending confirmation.',
        'processing': 'We are currently preparing your order.',
        'ready': 'Your order is ready for pickup/delivery!',
        'completed': 'Your order has been completed. Thank you for your business!',
        'cancelled': 'Your order has been cancelled.'
    }
    
    status_colors = {
        'pending': '#F59E0B',
        'processing': '#3B82F6',
        'ready': '#8B5CF6',
        'completed': '#10B981',
        'cancelled': '#EF4444'
    }
    
    status_msg = status_messages.get(order.status, f"Your order status is now: {order.status}")
    status_color = status_colors.get(order.status, '#6B7280')
    subject = f"Order Update: {order.order_number} - {order.get_status_display()}"
    
    # Render professional template
    from django.template.loader import render_to_string
    
    context = {
        'order': order,
        'status_message': status_msg,
        'status_color': status_color,
    }
    
    try:
        html_message = render_to_string('emails/order_status_update.html', context)
    except Exception as e:
        print(f"[Email Debug] Template rendering failed: {e}, using fallback")
        # Fallback to simple HTML
        html_message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">Order Update</h2>
            <p>Hello {order.customer.name},</p>
            <p><strong>{status_msg}</strong></p>
            <p>Order Number: {order.order_number}</p>
            <p>Status: <span style="font-weight: bold; color: {status_color};">{order.get_status_display().upper()}</span></p>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;" />
            <p style="color: #666; font-size: 12px;">{order.branch.name}</p>
        </div>
        """
    
    plain_message = strip_tags(html_message)

    try:
        print(f"[Email Debug] Sending to {order.customer.email} with subject: {subject}")
        
        # Use EmailMessage for better control over headers
        from django.core.mail import EmailMultiAlternatives
        import re
        
        # Determine sender - extract email if DEFAULT_FROM_EMAIL is formatted
        from_email_raw = settings.DEFAULT_FROM_EMAIL
        
        # Extract just the email address if it's in format "Name <email@domain.com>"
        email_match = re.search(r'<(.+?)>', from_email_raw)
        if email_match:
            from_email = email_match.group(1)
        else:
            from_email = from_email_raw
        
        from_name = order.branch.tenant.name
        
        # Format: "Company Name <email@domain.com>"
        formatted_from = f"{from_name} <{from_email}>"
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=formatted_from,
            to=[order.customer.email],
            reply_to=[from_email],
        )
        
        # Attach HTML version
        email.attach_alternative(html_message, "text/html")
        
        # Add headers to improve deliverability
        email.extra_headers = {
            'X-Entity-Ref-ID': str(order.id),
            'X-Mailer': 'Django',
            'Message-ID': f"<order-{order.order_number}-{order.status}@{order.branch.tenant.subdomain}.pos>",
            'List-Unsubscribe': f'<mailto:{from_email}?subject=Unsubscribe>',
            'Precedence': 'bulk',
            'X-Auto-Response-Suppress': 'OOF, AutoReply',
        }
        
        # Send the email
        email.send(fail_silently=False)
        
        print(f"[Email] Successfully sent status update to {order.customer.email}")
    except Exception as e:
        print(f"[Email Error] Failed to send customer email: {e}")
        import traceback
        traceback.print_exc()


