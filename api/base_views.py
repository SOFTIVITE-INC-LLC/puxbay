from rest_framework import viewsets, views
from rest_framework.response import Response

class StandardizedViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet that ensures all responses follow a consistent JSON envelope.
    """
    def finalize_response(self, request, response, *args, **kwargs):
        if isinstance(response, Response):
            # Define status based on HTTP code
            status_str = "success" if 200 <= response.status_code < 300 else "error"
            
            # Extract message from data if it exists, else default
            message = response.data.get('message') if isinstance(response.data, dict) else None
            if not message and status_str == "error":
                message = response.data.get('detail') if isinstance(response.data, dict) else "An error occurred"

            standard_envelope = {
                "status": status_str,
                "code": response.status_code,
                "data": response.data,
                "message": message or ("Operation successful" if status_str == "success" else "Operation failed")
            }
            response.data = standard_envelope
        return super().finalize_response(request, response, *args, **kwargs)

class StandardizedReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only version of the standardized ViewSet.
    """
    def finalize_response(self, request, response, *args, **kwargs):
        if isinstance(response, Response):
            status_str = "success" if 200 <= response.status_code < 300 else "error"
            
            standard_envelope = {
                "status": status_str,
                "code": response.status_code,
                "data": response.data,
                "message": "Operation successful" if status_str == "success" else "Operation failed"
            }
            response.data = standard_envelope
        return super().finalize_response(request, response, *args, **kwargs)
class StandardizedAPIView(views.APIView):
    """
    Base APIView that ensures all responses follow a consistent JSON envelope.
    """
    def finalize_response(self, request, response, *args, **kwargs):
        if isinstance(response, Response):
            status_str = "success" if 200 <= response.status_code < 300 else "error"
            
            # Message extraction
            message = None
            if isinstance(response.data, dict):
                message = response.data.get('message') or response.data.get('detail')
            
            standard_envelope = {
                "status": status_str,
                "code": response.status_code,
                "data": response.data,
                "message": message or ("Operation successful" if status_str == "success" else "Operation failed")
            }
            response.data = standard_envelope
        return super().finalize_response(request, response, *args, **kwargs)
