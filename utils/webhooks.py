import hmac
import hashlib
import json
import requests
import threading
from django.conf import settings
from accounts.models import WebhookEndpoint, WebhookEvent

class WebhookService:
    @staticmethod
    def trigger(tenant, event_type, payload):
        """
        Trigger a webhook event for a specific tenant.
        This spawns a background thread to avoid blocking the request cycle.
        """
        # Find all active endpoints for this tenant subscribed to this event
        endpoints = WebhookEndpoint.objects.filter(
            tenant=tenant,
            is_active=True,
            events__contains=event_type
        )
        
        for endpoint in endpoints:
            # Start asynchronous delivery
            thread = threading.Thread(
                target=WebhookService._send_request,
                args=(endpoint, event_type, payload)
            )
            thread.daemon = True # Ensure thread exits when process does
            thread.start()

    @staticmethod
    def _send_request(endpoint, event_type, payload):
        """Perform the actual HTTP POST request and log the result"""
        # 1. Prepare Payload
        full_payload = {
            'event': event_type,
            'data': payload,
            'timestamp': str(threading.get_ident()) # Just for unique ID in mock? No, use something better
        }
        
        json_payload = json.dumps(full_payload)
        
        # 2. Generate Signature
        signature = hmac.new(
            endpoint.secret.encode(),
            json_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'Content-Type': 'application/json',
            'X-Puxbay-Signature': signature,
            'X-Puxbay-Event': event_type,
            'User-Agent': 'Puxbay-Webhooks/1.0'
        }
        
        # 3. Send Request
        try:
            response = requests.post(
                endpoint.url, 
                data=json_payload, 
                headers=headers, 
                timeout=10
            )
            status_code = response.status_code
            response_body = response.text[:1000] # Limit log size
            error_message = None
        except requests.exceptions.RequestException as e:
            status_code = None
            response_body = None
            error_message = str(e)
            
        # 4. Log the result
        WebhookEvent.objects.create(
            endpoint=endpoint,
            event_type=event_type,
            payload=full_payload,
            status_code=status_code,
            response_body=response_body,
            error_message=error_message
        )
