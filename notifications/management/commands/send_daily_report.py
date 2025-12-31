from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum
from main.models import Order
from accounts.models import Branch, Tenant, UserProfile
from notifications.utils import send_notification
from datetime import timedelta

class Command(BaseCommand):
    help = 'Sends daily sales summary report to managers and admins'

    def handle(self, *args, **options):
        today = timezone.now().date()
        # For simplicity, let's assume "daily" means since beginning of today in server time
        # Or better, yesterday's full day if running at midnight.
        # Let's target "today" assuming it runs at 11:59PM or close to it, or strictly for "today's activity so far"
        
        start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        tenants = Tenant.objects.all()
        
        self.stdout.write(f"Generating reports for {tenants.count()} tenants...")
        
        for tenant in tenants:
            branches = Branch.objects.filter(tenant=tenant)
            
            tenant_total = 0
            branch_breakdown = []
            
            for branch in branches:
                daily_sales = Order.objects.filter(
                    branch=branch,
                    status='completed',
                    created_at__gte=start_of_day
                ).aggregate(total=Sum('total_amount'))['total'] or 0
                
                tenant_total += daily_sales
                branch_breakdown.append(f"- {branch.name}: ${daily_sales:.2f}")
                
            report_message = (
                f"Daily Sales Report for {today}\n\n"
                f"Total Revenue: ${tenant_total:.2f}\n\n"
                f"Branch Breakdown:\n" + "\n".join(branch_breakdown)
            )
            
            # Send to Admins
            admins = UserProfile.objects.filter(tenant=tenant, role__in=['admin', 'financial'])
            count = 0
            for profile in admins:
                send_notification(
                    user=profile.user,
                    title=f"Daily Sales Report - {today}",
                    message=report_message,
                    level='info',
                    category='sales',
                    link="/company/reports/financial/"
                )
                count += 1
                
            self.stdout.write(f"Sent report for {tenant.name} to {count} users.")
            
        self.stdout.write(self.style.SUCCESS('Successfully sent daily reports'))
