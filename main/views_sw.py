from django.http import HttpResponse
from django.conf import settings
import os

def service_worker(request):
    """
    Serves the service worker file from the static directory with the correct content type.
    This allows the SW to be registered at the root scope.
    """
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'sw.js')
    try:
        with open(sw_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type='application/javascript')
    except FileNotFoundError:
        return HttpResponse("Service Worker not found", status=404)
