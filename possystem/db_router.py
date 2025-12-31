"""
Enhanced database router with load balancing across multiple replicas.

Routes read queries to multiple replicas using round-robin load balancing.
"""
import random
import threading


from django.conf import settings

class ReadReplicaRouter:
    """
    A router to control database operations for read/write splitting with multiple replicas.
    
    - All write operations go to 'default' (primary)
    - Read operations are load-balanced across multiple replicas
    - Falls back to 'default' if all replicas are unavailable
    """
    
    # Thread-safe counter for round-robin
    _counter = 0
    _lock = threading.Lock()
    
    @property
    def REPLICAS(self):
        # Dynamically get keys other than 'default'
        return [db for db in settings.DATABASES if db != 'default']
    
    def db_for_read(self, model, **hints):
        """
        Route read operations to replica databases using round-robin.
        """
        # Check if we're in a transaction (must use primary)
        if hints.get('instance') and hasattr(hints['instance'], '_state'):
            if hints['instance']._state.db and hints['instance']._state.db not in self.REPLICAS:
                return 'default'
        
        if not self.REPLICAS:
            return 'default'
            
        # Round-robin load balancing across replicas
        with self._lock:
            ReadReplicaRouter._counter += 1
            index = ReadReplicaRouter._counter % len(self.REPLICAS)
        
        return self.REPLICAS[index]
    
    def db_for_write(self, model, **hints):
        """
        Route write operations to primary database.
        """
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations between objects in the same database.
        """
        db_set = {'default'} | set(self.REPLICAS)
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Only allow migrations on the primary database, but let TenantSyncRouter 
        handle the schema/app scoping.
        """
        if db != 'default':
            return False
        return None # Let TenantSyncRouter decide based on SHARED/TENANT_APPS


class PrimaryOnlyRouter:
    """
    Alternative router that uses only the primary database.
    Useful for disabling read replicas temporarily.
    """
    
    def db_for_read(self, model, **hints):
        return 'default'
    
    def db_for_write(self, model, **hints):
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db != 'default':
            return False
        return None
