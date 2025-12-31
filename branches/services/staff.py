from django.db import transaction
from django.utils import timezone
from branches.models import Shift
from accounts.models import UserProfile, Branch
from django.db.models import Sum, Count, Avg
from decimal import Decimal

class StaffService:
    def __init__(self, tenant):
        self.tenant = tenant

    def schedule_shift(self, staff_id, branch_id, start_time, end_time, role=None, notes=None):
        """
        Creates a new scheduled shift for a staff member.
        """
        try:
            staff = UserProfile.objects.get(id=staff_id, tenant=self.tenant)
            branch = Branch.objects.get(id=branch_id, tenant=self.tenant)
            
            shift = Shift.objects.create(
                tenant=self.tenant,
                branch=branch,
                staff=staff,
                start_time=start_time,
                end_time=end_time,
                role=role,
                notes=notes,
                status='scheduled'
            )
            return {'status': 'success', 'shift_id': str(shift.id)}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def check_in(self, shift_id):
        """
        Marks a shift as checked-in at the current time.
        """
        try:
            shift = Shift.objects.get(id=shift_id, tenant=self.tenant)
            shift.actual_start = timezone.now()
            shift.status = 'checked_in'
            shift.save()
            return {'status': 'success'}
        except Shift.DoesNotExist:
            return {'status': 'error', 'message': 'Shift not found'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def check_out(self, shift_id):
        """
        Marks a shift as completed and records end time.
        """
        try:
            shift = Shift.objects.get(id=shift_id, tenant=self.tenant)
            shift.actual_end = timezone.now()
            shift.status = 'completed'
            shift.save()
            return {'status': 'success'}
        except Shift.DoesNotExist:
            return {'status': 'error', 'message': 'Shift not found'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def get_staff_performance(self, staff_id, start_date, end_date):
        """
        Calculates performance metrics for a staff member over a period.
        Includes total sales, order count, and average order value.
        """
        from main.models import Order
        
        try:
            staff = UserProfile.objects.get(id=staff_id, tenant=self.tenant)
            
            orders = Order.objects.filter(
                tenant=self.tenant,
                cashier=staff,
                created_at__range=(start_date, end_date),
                status='completed'
            )
            
            metrics = orders.aggregate(
                total_sales=Sum('total_amount'),
                order_count=Count('id'),
                avg_order_value=Avg('total_amount')
            )
            
            # Get shift hours
            shifts = Shift.objects.filter(
                staff=staff,
                actual_start__isnull=False,
                actual_end__isnull=False,
                start_time__date__range=(start_date.date(), end_date.date())
            )
            
            total_duration_hours = Decimal('0.00')
            for shift in shifts:
                duration = shift.actual_end - shift.actual_start
                total_duration_hours += Decimal(str(duration.total_seconds() / 3600))
            
            sales_per_hour = Decimal('0.00')
            if total_duration_hours > 0 and metrics['total_sales']:
                sales_per_hour = metrics['total_sales'] / total_duration_hours

            return {
                'status': 'success',
                'metrics': {
                    'total_sales': metrics['total_sales'] or Decimal('0.00'),
                    'order_count': metrics['order_count'] or 0,
                    'avg_order_value': metrics['avg_order_value'] or Decimal('0.00'),
                    'total_hours': total_duration_hours,
                    'sales_per_hour': sales_per_hour
                }
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
