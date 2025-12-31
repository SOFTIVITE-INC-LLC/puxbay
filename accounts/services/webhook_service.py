"""
Webhook Service

Handles webhook delivery with HMAC signature generation and validation.
"""
import json
import requests
from django.conf import settings
from accounts.models import WebhookEndpoint, WebhookEvent
from api.security import generate_webhook_signature
import logging

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for delivering webhooks to registered endpoints"""
    
    @staticmethod
    def deliver_webhook(event_type: str, payload: dict, tenant=None):
        """
        Deliver webhook to all subscribed endpoints.
        
        Args:
            event_type: Type of event (e.g., 'order.created', 'inventory.low')
            payload: Event payload data
            tenant: Tenant object (optional, for tenant-specific webhooks)
        
        Returns:
            List of WebhookEvent objects representing delivery attempts
        """
        # Find all active endpoints subscribed to this event
        endpoints = WebhookEndpoint.objects.filter(
            is_active=True,
            events__contains=[event_type]
        )
        
        if tenant:
            endpoints = endpoints.filter(tenant=tenant)
        
        delivery_results = []
        
        for endpoint in endpoints:
            result = WebhookService._deliver_to_endpoint(
                endpoint=endpoint,
                event_type=event_type,
                payload=payload
            )
            delivery_results.append(result)
        
        return delivery_results
    
    @staticmethod
    def _deliver_to_endpoint(endpoint: WebhookEndpoint, event_type: str, payload: dict):
        """
        Deliver webhook to a single endpoint.
        
        Args:
            endpoint: WebhookEndpoint object
            event_type: Event type string
            payload: Event payload
        
        Returns:
            WebhookEvent object representing the delivery attempt
        """
        # Serialize payload
        payload_json = json.dumps(payload)
        payload_bytes = payload_json.encode('utf-8')
        
        # Generate signature
        signature = generate_webhook_signature(payload_bytes, endpoint.secret)
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature,
            'X-Event-Type': event_type,
            'User-Agent': 'POS-Webhook/1.0'
        }
        
        # Attempt delivery
        webhook_event = WebhookEvent(
            endpoint=endpoint,
            event_type=event_type,
            payload=payload,
            signature=signature
        )
        
        try:
            response = requests.post(
                endpoint.url,
                data=payload_json,
                headers=headers,
                timeout=10  # 10 second timeout
            )
            
            webhook_event.status_code = response.status_code
            webhook_event.response_body = response.text[:1000]  # Limit to 1000 chars
            
            if response.status_code >= 400:
                webhook_event.error_message = f"HTTP {response.status_code}: {response.text[:500]}"
                logger.warning(f"Webhook delivery failed: {endpoint.url} - {response.status_code}")
            else:
                logger.info(f"Webhook delivered successfully: {endpoint.url} - {event_type}")
        
        except requests.exceptions.Timeout:
            webhook_event.error_message = "Request timeout after 10 seconds"
            logger.error(f"Webhook timeout: {endpoint.url}")
        
        except requests.exceptions.RequestException as e:
            webhook_event.error_message = f"Request failed: {str(e)}"
            logger.error(f"Webhook delivery error: {endpoint.url} - {str(e)}")
        
        except Exception as e:
            webhook_event.error_message = f"Unexpected error: {str(e)}"
            logger.error(f"Webhook unexpected error: {endpoint.url} - {str(e)}")
        
        finally:
            webhook_event.save()
        
        return webhook_event
    
    @staticmethod
    def test_webhook(endpoint_id: str):
        """
        Send a test webhook to verify endpoint configuration.
        
        Args:
            endpoint_id: UUID of the WebhookEndpoint
        
        Returns:
            WebhookEvent object
        """
        from accounts.models import WebhookEndpoint
        endpoint = WebhookEndpoint.objects.get(id=endpoint_id)
        
        test_payload = {
            'event': 'webhook.test',
            'message': 'This is a test webhook',
            'timestamp': str(datetime.datetime.now())
        }
        
        return WebhookService._deliver_to_endpoint(
            endpoint=endpoint,
            event_type='webhook.test',
            payload=test_payload
        )


# Example usage in your application:
# from accounts.services.webhook_service import WebhookService
# 
# # When an order is created:
# WebhookService.deliver_webhook(
#     event_type='order.created',
#     payload={
#         'order_id': str(order.id),
#         'total': float(order.total_amount),
#         'customer': order.customer.name
#     },
#     tenant=order.tenant
# )
