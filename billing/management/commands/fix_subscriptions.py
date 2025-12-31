from django.core.management.base import BaseCommand
from billing.models import Subscription
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Fix existing subscriptions missing current_period_end dates'

    def handle(self, *args, **options):
        # Get all active or trialing subscriptions without current_period_end
        subscriptions = Subscription.objects.filter(
            status__in=['active', 'trialing'],
            current_period_end__isnull=True
        )

        count = subscriptions.count()
        self.stdout.write(f"Found {count} subscriptions to fix\n")

        fixed = 0
        skipped = 0

        for sub in subscriptions:
            if sub.plan:
                # Calculate period end based on plan interval
                if sub.plan.interval == 'monthly':
                    period_end = timezone.now() + timedelta(days=30)
                elif sub.plan.interval == '6-month':
                    period_end = timezone.now() + timedelta(days=180)
                elif sub.plan.interval == 'yearly':
                    period_end = timezone.now() + timedelta(days=365)
                else:
                    period_end = timezone.now() + timedelta(days=30)  # Default to monthly
                
                sub.current_period_end = period_end
                sub.save()
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Fixed subscription for {sub.tenant.name} - expires {period_end}")
                )
                fixed += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"✗ Skipped subscription for {sub.tenant.name} - no plan assigned")
                )
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(f"\n✅ Done! Fixed {fixed} subscriptions, skipped {skipped}")
        )
