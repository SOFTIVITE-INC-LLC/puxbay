import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from main.models import Expense, ExpenseCategory
from accounts.models import UserProfile, Tenant

def check_expenses():
    print(f"Current Server Time: {timezone.now()}")
    print(f"Current Date: {timezone.now().date()}")

    print("\n--- Tenants ---")
    for t in Tenant.objects.all():
        print(f"ID: {t.id} Name: {t.name} Subdomain: {t.subdomain}")

    print("\n--- Expenses ---")
    expenses = Expense.objects.all()
    if not expenses.exists():
        print("No expenses found in database.")
    
    for e in expenses:
        print(f"ID: {e.id}, Tenant: {e.tenant.name} ({e.tenant.id}), Amount: {e.amount}, Date: {e.date}, Category: {e.category.name}")
        
        # Check if it falls in 'month' range
        today = timezone.now().date()
        start_date = today - timezone.timedelta(days=30)
        
        in_range = start_date <= e.date <= today
        print(f"  -> In last 30 days ({start_date} to {today})? {in_range}")

if __name__ == '__main__':
    check_expenses()
