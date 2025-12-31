import sys
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Tenant, UserProfile, Branch, Attendance, ActivityLog
from billing.models import Subscription, Payment, Plan

class Command(BaseCommand):
    help = 'Clean users, tenants, and subscriptions from the database for fresh testing.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("⚠️  WARNING: This will delete ALL data except Plans!"))
        
        # Check if running in a terminal that supports input
        if sys.stdin.isatty():
            confirm = input("Are you absolutely sure? (y/N): ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.NOTICE("Cleanup cancelled."))
                return

        # 1. Delete logs (Shared)
        ActivityLog.objects.all().delete()
        Attendance.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✓ Deleted all logs (Shared)"))

        # 2. Delete billing data (Shared)
        Payment.objects.all().delete()
        Subscription.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✓ Deleted billing data (Shared)"))

        # 3. Delete entities (Shared)
        # Note: Deleting Tenants will automatically drop their respective schemas and all data within them (Product, Order, etc.)
        Branch.objects.all().delete()
        UserProfile.objects.all().delete()
        Tenant.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(self.style.SUCCESS("=" * 40))
        self.stdout.write(self.style.SUCCESS("DATABASE CLEANUP COMPLETE!"))
        self.stdout.write(self.style.SUCCESS("=" * 40))
