"""
Webhooks resource client
"""

from typing import Dict, Any, Optional, List


class Webhooks:
    """Client for webhook-related API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def list(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """List all webhook endpoints"""
        return self.client.get('webhooks/', params={'page': page, 'page_size': page_size})
    
    def get(self, webhook_id: str) -> Dict[str, Any]:
        """Get a specific webhook endpoint by ID"""
        return self.client.get(f'webhooks/{webhook_id}/')
    
    def create(self, url: str, events: List[str], secret: Optional[str] = None) -> Dict[str, Any]:
        """Create a new webhook endpoint"""
        data = {'url': url, 'events': events}
        if secret:
            data['secret'] = secret
        return self.client.post('webhooks/', json=data)
    
    def update(self, webhook_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing webhook endpoint"""
        return self.client.patch(f'webhooks/{webhook_id}/', json=data)
    
    def delete(self, webhook_id: str) -> Dict[str, Any]:
        """Delete a webhook endpoint"""
        return self.client.delete(f'webhooks/{webhook_id}/')
    
    def list_events(self, webhook_id: str, page: int = 1) -> Dict[str, Any]:
        """List webhook delivery events"""
        return self.client.get(f'webhook-logs/', params={'webhook': webhook_id, 'page': page})
