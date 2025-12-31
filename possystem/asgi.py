import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from possystem.middleware_asgi import TenantMiddleware
import possystem.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TenantMiddleware(
        AuthMiddlewareStack(
            URLRouter(
                possystem.routing.websocket_urlpatterns
            )
        )
    ),
})
