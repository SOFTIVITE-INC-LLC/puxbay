"""
Management command to test database replica connectivity and routing.

Usage:
    python manage.py test_replica
"""
from django.core.management.base import BaseCommand
from django.db import connections
from main.models import Product
from django.db.models import Count


class Command(BaseCommand):
    help = 'Test database replica connectivity and routing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Testing Database Replica Setup'))
        self.stdout.write('=' * 50)
        
        # Test primary connection
        self.stdout.write('\n1. Testing PRIMARY database connection...')
        try:
            conn = connections['default']
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f'   ✓ Primary connected: {version[:50]}...'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Primary connection failed: {e}'))
            return
        
        # Test replica connection
        self.stdout.write('\n2. Testing REPLICA database connection...')
        try:
            conn = connections['replica']
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f'   ✓ Replica connected: {version[:50]}...'))
                
                # Check if in recovery mode (standby)
                cursor.execute("SELECT pg_is_in_recovery();")
                is_standby = cursor.fetchone()[0]
                if is_standby:
                    self.stdout.write(self.style.SUCCESS('   ✓ Replica is in recovery mode (standby)'))
                else:
                    self.stdout.write(self.style.WARNING('   ⚠ Replica is NOT in recovery mode (might be primary)'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Replica connection failed: {e}'))
            self.stdout.write(self.style.WARNING('   → Falling back to primary for all operations'))
        
        # Test read routing
        self.stdout.write('\n3. Testing READ query routing...')
        try:
            # This should use replica
            products = Product.objects.all()[:5]
            count = products.count()
            
            # Check which database was used
            if products.db == 'replica':
                self.stdout.write(self.style.SUCCESS(f'   ✓ Read query used REPLICA database ({count} products)'))
            else:
                self.stdout.write(self.style.WARNING(f'   ⚠ Read query used PRIMARY database ({count} products)'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Read query failed: {e}'))
        
        # Test write routing
        self.stdout.write('\n4. Testing WRITE query routing...')
        try:
            # Create a test query (won't actually execute)
            from django.db import router
            test_product = Product()
            db_for_write = router.db_for_write(Product, instance=test_product)
            
            if db_for_write == 'default':
                self.stdout.write(self.style.SUCCESS('   ✓ Write queries will use PRIMARY database'))
            else:
                self.stdout.write(self.style.ERROR(f'   ✗ Write queries using wrong database: {db_for_write}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ✗ Write routing test failed: {e}'))
        
        # Test replication lag
        self.stdout.write('\n5. Checking replication lag...')
        try:
            conn = connections['default']
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT client_addr, state, sync_state, 
                           COALESCE(replay_lag, '0 seconds'::interval) as replay_lag
                    FROM pg_stat_replication;
                """)
                replicas = cursor.fetchall()
                
                if replicas:
                    for replica in replicas:
                        addr, state, sync_state, lag = replica
                        self.stdout.write(self.style.SUCCESS(
                            f'   ✓ Replica {addr}: {state}, {sync_state}, lag: {lag}'
                        ))
                else:
                    self.stdout.write(self.style.WARNING('   ⚠ No replication connections found'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'   ⚠ Could not check replication: {e}'))
        
        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('\n✓ Database replica test complete!'))
        self.stdout.write('\nConfiguration:')
        self.stdout.write(f'  Primary:  {connections["default"].settings_dict["HOST"]}:{connections["default"].settings_dict["PORT"]}')
        self.stdout.write(f'  Replica:  {connections["replica"].settings_dict["HOST"]}:{connections["replica"].settings_dict["PORT"]}')
        self.stdout.write('\nRouting:')
        self.stdout.write('  Read queries  → Replica')
        self.stdout.write('  Write queries → Primary')
        self.stdout.write('')
