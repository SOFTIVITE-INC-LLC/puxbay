from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='currency')
def currency(value, symbol=None):
    """
    Format a number as currency with the appropriate symbol.
    Usage: {{ amount|currency }} or {{ amount|currency:"€" }}
    """
    if value is None or value == '':
        return f"{symbol or '$'}0.00"
    
    try:
        # Convert to Decimal for precise formatting
        if isinstance(value, str):
            value = Decimal(value)
        elif not isinstance(value, Decimal):
            value = Decimal(str(value))
        
        # Format with 2 decimal places and thousand separators
        formatted = f"{value:,.2f}"
        
        # Use provided symbol or default
        currency_symbol = symbol or '$'
        
        return f"{currency_symbol}{formatted}"
    except (ValueError, TypeError, ArithmeticError):
        return f"{symbol or '$'}0.00"


@register.filter(name='branch_currency')
def branch_currency(value, branch=None):
    """
    Format a number with the branch's currency symbol.
    Usage: {{ amount|branch_currency:branch }}
    """
    if branch and hasattr(branch, 'currency_symbol'):
        return currency(value, branch.currency_symbol)
    return currency(value)


@register.simple_tag(takes_context=True)
def format_currency(context, value):
    """
    Template tag to format currency using branch context.
    Usage: {% format_currency amount %}
    """
    symbol = context.get('branch_currency_symbol', '$')
    return currency(value, symbol)
