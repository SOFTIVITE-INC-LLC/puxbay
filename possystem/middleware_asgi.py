
from channels.middleware import BaseMiddleware
from django.db import close_old_connections
from channels.db import database_sync_to_async
from django_tenants.utils import get_tenant_model, get_public_schema_name

class TenantMiddleware(BaseMiddleware):
    """
    Middleware to set the tenant schema for the ASGI scope based on the host header.
    This ensures that subsequent middleware (like AuthMiddleware) and consumers
    operate within the correct tenant context.
    """
    async def __call__(self, scope, receive, send):
        # Close old connections to prevent leaking 
        await database_sync_to_async(close_old_connections)()
        
        hostname = None
        # Extract hostname from headers
        for name, value in scope.get("headers", []):
            if name == b"host":
                hostname = value.decode("latin1").split(":")[0]
                break
        
        if hostname:
            tenant = await self.get_tenant_from_hostname(hostname)
            if tenant:
                scope["tenant"] = tenant
                # Set the schema for this context
                # Note: This sets it for the thread running this async code.
                # Since channels runs consumers in thread pools, we need to be careful.
                # However, AuthMiddleware uses database_sync_to_async which runs in a thread.
                # We need to ensure the schema is set when those threads run.
                
                # Unlike WSGI, we can't just set it globally. 
                # But django-tenants monkey patches the DB backend.
                # We mainly put the tenant in scope so consumers can use it.
                
                # For DB access to work in AuthMiddleware/SessionMiddleware, we might need 
                # to set connection.set_schema(tenant.schema_name) inside a sync wrapper 
                # if those middlewares strictly rely on it.
                pass
        
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_tenant_from_hostname(self, hostname):
        from django.db import connection
        try:
            # Logic to resolve tenant from hostname
            # This mimics SubdomainMiddleware logic but for ASGI
            parts = hostname.split('.')
            subdomain = parts[0]
            
            tenant_model = get_tenant_model()
            
            # Localhost handling
            if 'localhost' in hostname and len(parts) == 2:
                # subdomain.localhost
                subdomain = parts[0]
            elif len(parts) < 3:
                # likely just domain.com or localhost
                subdomain = None
            
            if subdomain and subdomain != 'www':
                try:
                    tenant = tenant_model.objects.get(subdomain=subdomain)
                    connection.set_tenant(tenant)
                    return tenant
                except tenant_model.DoesNotExist:
                    pass
            
            # Default to public if not found (or return public tenant object if you have one)
            # Ensure connection is set to public
            connection.set_schema_to_public()
            return None
            
        except Exception as e:
            print(f"ASGI Tenant Resolution Error: {e}")
            return None
