from django.db.models import Sum
from main.models import Order
from branches.models import Shift
from branches.models_workforce import CommissionRule, StaffAchievement
from decimal import Decimal
import datetime

class GamificationService:
    def __init__(self, tenant):
        self.tenant = tenant

    def calculate_commissions(self, staff_profile, start_date=None, end_date=None):
        """Calculates tiered payouts based on commission rules for a specific staff member"""
        if not start_date:
            start_date = datetime.date.today().replace(day=1) # Default to start of month
        if not end_date:
            end_date = datetime.date.today()

        # Sum sales for this staff member
        total_sales = Order.objects.filter(
            tenant=self.tenant,
            cashier=staff_profile,
            created_at__date__range=[start_date, end_date],
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        # Find applicable rules
        rules = CommissionRule.objects.filter(
            tenant=self.tenant,
            is_active=True,
            min_sales_amount__lte=total_sales
        ).order_by('-min_sales_amount')

        commission_amount = Decimal('0.00')
        rule_applied = None

        if rules.exists():
            rule = rules.first() # Highest tier attained
            rule_applied = rule
            commission_amount = (total_sales * (rule.commission_percentage / 100)) + rule.flat_bonus

        return {
            'total_sales': total_sales,
            'commission_amount': commission_amount,
            'rule_applied': rule_applied,
            'start_date': start_date,
            'end_date': end_date
        }

    def evaluate_achievements(self, staff_profile):
        """Checks criteria and awards badges to staff"""
        new_badges = []
        
        # 1. "Top Performer" - reached $1000 sales this month
        month_start = datetime.date.today().replace(day=1)
        sales = Order.objects.filter(
            cashier=staff_profile,
            created_at__date__gte=month_start,
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        if sales >= 1000 and not StaffAchievement.objects.filter(staff=staff_profile, badge_name="Top Performer").exists():
            badge = StaffAchievement.objects.create(
                staff=staff_profile,
                badge_name="Top Performer",
                badge_icon="emoji_events",
                description="Reached $1,000 in sales this month!"
            )
            new_badges.append(badge)

        # 2. "Punctual" - completed 5 shifts with actual_start <= start_time
        # (Assuming Shift model has start_time and actual_start)
        # For simplicity, let's just use a count for now if criteria met
        shifts_count = Shift.objects.filter(
            staff=staff_profile,
            actual_start__isnull=False
        ).count()
        
        if shifts_count >= 5 and not StaffAchievement.objects.filter(staff=staff_profile, badge_name="Reliable").exists():
            badge = StaffAchievement.objects.create(
                staff=staff_profile,
                badge_name="Reliable",
                badge_icon="verified",
                description="Completed 5 shifts!"
            )
            new_badges.append(badge)

        return new_badges
