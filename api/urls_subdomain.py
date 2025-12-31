from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Support both prefixed and non-prefixed access
    path('v1/', include('api.urls')),
    path('v1/', include('api.urls')),
]
