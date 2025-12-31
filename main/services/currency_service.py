"""
Currency Service for exchange rate management and conversion.
"""
from decimal import Decimal
from main.models import Currency
from django.core.cache import cache
import requests

BASE_CURRENCY = 'USD'

def get_exchange_rate(target_currency_code):
    """
    Get exchange rate for target currency relative to USD.
    Returns 1.0 if target is USD or not found.
    """
    if target_currency_code == BASE_CURRENCY:
        return Decimal('1.0')
        
    # Try cache first
    cache_key = f'exchange_rate_{target_currency_code}'
    rate = cache.get(cache_key)
    if rate:
        return Decimal(rate)
    
    # Try database
    try:
        currency = Currency.objects.get(code=target_currency_code, is_active=True)
        # Cache for 1 hour
        cache.set(cache_key, str(currency.exchange_rate), 3600)
        return currency.exchange_rate
    except Currency.DoesNotExist:
        return Decimal('1.0')

def convert_currency(amount, from_currency, to_currency):
    """
    Convert amount from one currency to another.
    """
    if from_currency == to_currency:
        return amount
        
    amount = Decimal(str(amount))
    
    # Convert to base (USD) first
    from_rate = get_exchange_rate(from_currency)
    to_rate = get_exchange_rate(to_currency)
    
    # Amount in USD = Amount / From_Rate
    amount_in_usd = amount / from_rate
    
    # Amount in Target = Amount in USD * To_Rate
    final_amount = amount_in_usd * to_rate
    
    return final_amount.quantize(Decimal('0.01'))

def update_exchange_rates(rates=None):
    """
    Update database with provided rates or fetch from API if not provided.
    """
    from datetime import datetime
    
    if rates is None:
        api_url = f"https://api.exchangerate-api.com/v4/latest/{BASE_CURRENCY}"
        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                rates = response.json().get('rates', {})
        except Exception as e:
            print(f"Error fetching rates: {e}")
            return False

    if rates:
        # Only update existing currencies to keep things clean
        for code, rate in rates.items():
            Currency.objects.filter(code=code).update(
                exchange_rate=Decimal(str(rate)),
                last_updated=datetime.now()
            )
        return True
    return False
