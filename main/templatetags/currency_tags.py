from django import template
from decimal import Decimal
from main.services.currency_service import convert_currency, get_exchange_rate

register = template.Library()

@register.filter
def to_currency(value, currency_code='USD'):
    """
    Convert value to target currency.
    Usage: {{ price|to_currency:'EUR' }}
    """
    if value is None or value == "":
        return ""
    
    # Default source is USD (base)
    # If we need dynamic source, we need to pass it or infer it
    # For now assuming value is in Base Currency (USD)
    
    try:
        converted = convert_currency(value, 'USD', currency_code)
        return f"{converted:,.2f}"
    except Exception:
        return value

@register.filter
def currency_symbol(code):
    """Get symbol for currency code"""
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'NGN': '₦',
        'GHS': '₵',
        'ZAR': 'R',
    }
    return symbols.get(code, code)

@register.simple_tag(takes_context=True)
def current_currency(context):
    """Get current currency from session or user preferences"""
    request = context.get('request')
    if not request:
        return 'USD'
        
    return request.session.get('currency', 'USD')
