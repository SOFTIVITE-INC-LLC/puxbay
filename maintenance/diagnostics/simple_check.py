import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from billing.utils import is_subscription_active
from accounts.models import Tenant

for t in Tenant.objects.all():
    try:
        active = is_subscription_active(t)
        print(f"{t.name}: {active}")
    except:
        print(f"{t.name}: ERROR")
