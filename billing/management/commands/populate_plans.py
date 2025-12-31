from django.core.management.base import BaseCommand
from billing.models import Plan

class Command(BaseCommand):
    help = 'Populates the database with initial subscription plans provided'

    def handle(self, *args, **kwargs):
        # Clear existing plans to ensure the new structure is applied correctly
        Plan.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing plans.'))

        intervals = [
            ('monthly', 'Monthly'),
            ('6-month', '6 Months'),
            ('yearly', 'Yearly'),
        ]

        tiers = [
            {
                'level': 'Starter',
                'price_base': 19.00,
                'max_branches': 1,
                'max_users': 3,
                'desc': 'Perfect for small shops.'
            },
            {
                'level': 'Professional',
                'price_base': 49.00,
                'max_branches': 3,
                'max_users': 10,
                'desc': 'Ideal for growing businesses.'
            },
            {
                'level': 'Business',
                'price_base': 99.00,
                'max_branches': 10,
                'max_users': 50,
                'desc': 'For established multi-branch stores.'
            },
            {
                'level': 'Ultimate',
                'price_base': 249.00,
                'max_branches': 100,
                'max_users': 1000,
                'desc': 'Enterprise-grade features and scaling.'
            },
        ]

        # Multipliers based on interval (to give slight discounts for longer periods)
        interval_configs = {
            'monthly': {'multiplier': 1, 'gh_multiplier': 15},
            '6-month': {'multiplier': 5, 'gh_multiplier': 15},  # Pay for 5 months, get 6
            'yearly': {'multiplier': 10, 'gh_multiplier': 15}, # Pay for 10 months, get 12
        }

        for interval_slug, interval_name in intervals:
            config = interval_configs[interval_slug]
            for tier in tiers:
                plan_name = f"{tier['level']} ({interval_name})"
                price_usd = tier['price_base'] * config['multiplier']
                price_ghs = price_usd * config['gh_multiplier']

                # Define specific feature descriptions instead of booleans
                if tier['level'] == 'Starter':
                    features = {
                        'pos_access': 'Standard POS Access',
                        'inventory': 'Basic tracking',
                        'reports': 'Daily summary only',
                        'support': 'Email support',
                        'api': 'Not included'
                    }
                elif tier['level'] == 'Professional':
                    features = {
                        'pos_access': 'Standard POS Access',
                        'inventory': 'Advanced tracking & variants',
                        'reports': 'Full analytics suite',
                        'support': 'Priority Email & Chat',
                        'api': 'Basic access (1,000/day)'
                    }
                elif tier['level'] == 'Business':
                    features = {
                        'pos_access': 'Unlimited Terminal Access',
                        'inventory': 'Multi-location management',
                        'reports': 'Custom Financial P&L',
                        'support': '24/7 Priority Support',
                        'api': 'Advanced access (10,000/day)'
                    }
                else:  # Ultimate
                    features = {
                        'pos_access': 'Priority Terminal Access',
                        'inventory': 'Enterprise Supply Chain',
                        'reports': 'AI Intelligence Reports',
                        'support': 'Dedicated Account Manager',
                        'api': 'Unlimited API Access'
                    }

                Plan.objects.create(
                    name=plan_name,
                    price=price_usd,
                    price_ghs=price_ghs,
                    interval=interval_slug,
                    description=tier['desc'],
                    max_branches=tier['max_branches'],
                    max_users=tier['max_users'],
                    is_active=True,
                    features=features
                )
                self.stdout.write(self.style.SUCCESS(f"Created: {plan_name} - ${price_usd} / GHS {price_ghs}"))

        self.stdout.write(self.style.SUCCESS('Successfully populated 12 subscription plans.'))
