from django.core.management.base import BaseCommand
from main.models import Currency
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seeds initial currency data'

    def handle(self, *args, **kwargs):
        currencies = [
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'rate': '1.0'},
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'rate': '0.92'},
            {'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'rate': '0.79'},
            {'code': 'NGN', 'name': 'Nigerian Naira', 'symbol': '₦', 'rate': '1600.0'},
            {'code': 'GHS', 'name': 'Ghanaian Cedi', 'symbol': '₵', 'rate': '15.5'},
            {'code': 'ZAR', 'name': 'South African Rand', 'symbol': 'R', 'rate': '18.5'},
        ]
        
        for curr in currencies:
            Currency.objects.update_or_create(
                code=curr['code'],
                defaults={
                    'name': curr['name'],
                    'symbol': curr['symbol'],
                    'exchange_rate': Decimal(curr['rate']),
                    'is_active': True
                }
            )
            
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(currencies)} currencies'))
