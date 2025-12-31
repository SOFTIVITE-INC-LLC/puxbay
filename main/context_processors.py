from main.models import Currency

def currency_processor(request):
    """
    Context processor to make available currencies and active currency
    accessible in all templates.
    """
    from django.db import connection
    
    # Check if we're in public schema - skip currency processing
    schema_name = getattr(connection, 'schema_name', 'public')
    if schema_name == 'public':
        return {
            'available_currencies': [],
            'current_currency_code': 'GHS',
            'current_currency': {'code': 'GHS', 'symbol': 'GH₵', 'exchange_rate': 12.0, 'name': 'Ghanaian Cedi'},
        }
    
    # Only import Currency model if not in public schema
    from main.models import Currency
    
    # Get active currency from session or default to USD
    current_code = request.session.get('currency', 'GHS')
    
    # Get all active currencies
    try:
        currencies = list(Currency.objects.filter(is_active=True).values('code', 'symbol', 'name', 'exchange_rate'))
    except:
        # Fallback if Currency table doesn't exist
        currencies = []
    
    # Get current currency object
    curr_obj = next((c for c in currencies if c['code'] == current_code), None)
    if not curr_obj:
        # Fallback to GHS if session currency not found
        curr_obj = next((c for c in currencies if c['code'] == 'GHS'), {'code': 'GHS', 'symbol': 'GH₵', 'exchange_rate': 12.0, 'name': 'Ghanaian Cedi'})

    return {
        'available_currencies': currencies,
        'current_currency_code': current_code,
        'current_currency': curr_obj,
    }
