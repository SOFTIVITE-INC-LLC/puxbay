"""
Purchase Orders resource client
"""

from typing import Dict, Any, Optional


class PurchaseOrders:
    """Client for purchase order-related API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def list(self, page: int = 1, page_size: int = 20, status: Optional[str] = None) -> Dict[str, Any]:
        """List all purchase orders"""
        params = {'page': page, 'page_size': page_size}
        if status:
            params['status'] = status
        return self.client.get('purchase-orders/', params=params)
    
    def get(self, po_id: str) -> Dict[str, Any]:
        """Get a specific purchase order by ID"""
        return self.client.get(f'purchase-orders/{po_id}/')
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new purchase order"""
        return self.client.post('purchase-orders/', json=data)
    
    def update(self, po_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing purchase order"""
        return self.client.patch(f'purchase-orders/{po_id}/', json=data)
    
    def receive(self, po_id: str, items: list) -> Dict[str, Any]:
        """Receive items from a purchase order"""
        return self.client.post(f'purchase-orders/{po_id}/receive/', json={'items': items})
