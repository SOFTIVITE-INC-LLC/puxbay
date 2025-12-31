"""
Debug script to check if Celery tasks are being queued properly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from celery import current_app
from django.core.cache import cache

print("=" * 70)
print("CELERY CONFIGURATION CHECK")
print("=" * 70)

# Check Celery configuration
print(f"\n📋 Celery App: {current_app}")
print(f"   Broker: {current_app.conf.broker_url}")
print(f"   Backend: {current_app.conf.result_backend}")

# Try to inspect active tasks
try:
    inspect = current_app.control.inspect()
    
    print("\n🔍 Active Tasks:")
    active = inspect.active()
    if active:
        for worker, tasks in active.items():
            print(f"   Worker: {worker}")
            for task in tasks:
                print(f"      - {task['name']} (ID: {task['id']})")
    else:
        print("   No active tasks")
    
    print("\n📝 Registered Tasks:")
    registered = inspect.registered()
    if registered:
        for worker, tasks in registered.items():
            print(f"   Worker: {worker}")
            for task in tasks:
                if 'import_products' in task:
                    print(f"      ✓ {task}")
    else:
        print("   ⚠️  No workers responding!")
        
except Exception as e:
    print(f"   ❌ Error inspecting Celery: {e}")
    print("   Is the Celery worker running?")

# Check if we can import the task
print("\n🔧 Task Import Check:")
try:
    from branches.tasks import import_products_task
    print(f"   ✓ Task imported: {import_products_task}")
    print(f"   ✓ Task name: {import_products_task.name}")
except Exception as e:
    print(f"   ❌ Failed to import task: {e}")

# Test a simple task
print("\n🧪 Testing Simple Task Execution:")
try:
    from celery import shared_task
    
    @shared_task
    def test_task():
        return "Hello from Celery!"
    
    result = test_task.delay()
    print(f"   ✓ Task queued: {result.id}")
    print(f"   ⏳ Waiting for result...")
    
    try:
        output = result.get(timeout=5)
        print(f"   ✅ Task completed: {output}")
    except Exception as e:
        print(f"   ❌ Task failed or timed out: {e}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
