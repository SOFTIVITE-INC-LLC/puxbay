"""
Alert Service for managing stock alerts.
Handles detection, creation, and notification of low stock alerts.
"""
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from main.models import Product, StockAlert


def check_stock_levels(branch=None):
    """
    Check stock levels for all products and create alerts if needed.
    
    Args:
        branch: Optional branch to check. If None, checks all products.
    
    Returns:
        List of created alerts
    """
    alerts_created = []
    
    # Get products to check
    products = Product.objects.filter(is_active=True, alert_enabled=True)
    if branch:
        products = products.filter(branch=branch)
    
    for product in products:
        # Check if product already has an unresolved alert
        existing_alert = StockAlert.objects.filter(
            product=product,
            is_resolved=False
        ).first()
        
        if existing_alert:
            continue  # Skip if alert already exists
        
        # Determine alert type
        alert_type = None
        if product.stock_quantity == 0:
            alert_type = 'out_of_stock'
        elif product.stock_quantity <= product.low_stock_threshold:
            alert_type = 'low_stock'
        
        if alert_type:
            alert = create_alert(product, alert_type)
            alerts_created.append(alert)
    
    return alerts_created


def create_alert(product, alert_type):
    """
    Create a stock alert for a product.
    
    Args:
        product: Product instance
        alert_type: 'low_stock' or 'out_of_stock'
    
    Returns:
        Created StockAlert instance
    """
    alert = StockAlert.objects.create(
        product=product,
        alert_type=alert_type,
        threshold=product.low_stock_threshold,
        current_stock=product.stock_quantity
    )
    
    # Send notification email
    send_alert_email(alert)
    
    return alert


def send_alert_email(alert):
    """
    Send email notification for a stock alert.
    
    Args:
        alert: StockAlert instance
    """
    if alert.notified:
        return  # Already notified
    
    try:
        product = alert.product
        tenant = product.tenant
        
        # Get tenant admin emails
        admin_emails = tenant.userprofile_set.filter(
            user__is_staff=True
        ).values_list('user__email', flat=True)
        
        if not admin_emails:
            return
        
        subject = f"{settings.EMAIL_SUBJECT_PREFIX}Stock Alert: {product.name}"
        
        context = {
            'alert': alert,
            'product': product,
            'tenant': tenant,
            'alert_type_display': alert.get_alert_type_display(),
        }
        
        html_message = render_to_string('emails/stock_alert.html', context)
        plain_message = f"""
Stock Alert: {alert.get_alert_type_display()}

Product: {product.name}
SKU: {product.sku}
Current Stock: {alert.current_stock}
Threshold: {alert.threshold}
Branch: {product.branch.name}

Please restock this item as soon as possible.
        """
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            list(admin_emails),
            html_message=html_message,
            fail_silently=True,
        )
        
        alert.notified = True
        alert.save()
        
    except Exception as e:
        print(f"Error sending alert email: {e}")


def resolve_alert(alert_id):
    """
    Resolve a stock alert.
    
    Args:
        alert_id: UUID of the alert to resolve
    
    Returns:
        Resolved StockAlert instance or None
    """
    try:
        alert = StockAlert.objects.get(id=alert_id)
        alert.resolve()
        return alert
    except StockAlert.DoesNotExist:
        return None


def get_active_alerts(branch=None, limit=None):
    """
    Get active (unresolved) stock alerts.
    
    Args:
        branch: Optional branch to filter by
        limit: Optional limit on number of alerts
    
    Returns:
        QuerySet of StockAlert instances
    """
    alerts = StockAlert.objects.filter(is_resolved=False).select_related('product', 'product__branch')
    
    if branch:
        alerts = alerts.filter(product__branch=branch)
    
    if limit:
        alerts = alerts[:limit]
    
    return alerts


def get_alert_summary(branch=None):
    """
    Get summary statistics for stock alerts.
    
    Args:
        branch: Optional branch to filter by
    
    Returns:
        Dictionary with alert statistics
    """
    alerts = StockAlert.objects.filter(is_resolved=False)
    
    if branch:
        alerts = alerts.filter(product__branch=branch)
    
    return {
        'total_alerts': alerts.count(),
        'low_stock_count': alerts.filter(alert_type='low_stock').count(),
        'out_of_stock_count': alerts.filter(alert_type='out_of_stock').count(),
        'unnotified_count': alerts.filter(notified=False).count(),
    }
