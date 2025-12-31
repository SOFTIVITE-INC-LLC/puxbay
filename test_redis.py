"""
Test Redis connectivity
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from django.conf import settings

print("=" * 70)
print("REDIS CONNECTIVITY TEST")
print("=" * 70)

# Check Redis URL from settings
redis_url = settings.REDIS_URL
print(f"\n📍 Redis URL: {redis_url}")

# Try to connect to Redis
print("\n🔌 Testing Redis connection...")
try:
    import redis
    r = redis.from_url(redis_url)
    r.ping()
    print("   ✅ Redis is running and accessible!")
    
    # Check if there are any pending tasks
    print("\n📋 Checking Celery queues...")
    celery_queue = r.llen('celery')
    print(f"   Celery queue length: {celery_queue}")
    
    if celery_queue > 0:
        print(f"   ⚠️  There are {celery_queue} pending tasks in the queue!")
    
except ImportError:
    print("   ❌ Redis package not installed!")
    print("   Run: pip install redis")
except Exception as e:
    print(f"   ❌ Cannot connect to Redis: {e}")
    print("\n   💡 Solutions:")
    print("      1. Start Redis: redis-server")
    print("      2. Or install Redis for Windows")
    print("      3. Or use a different broker (RabbitMQ, etc.)")

print("\n" + "=" * 70)
