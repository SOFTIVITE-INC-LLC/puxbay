"""
Suppliers resource client
"""

from typing import Dict, Any, Optional


class Suppliers:
    """Client for supplier-related API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def list(self, page: int = 1, page_size: int = 20, search: Optional[str] = None) -> Dict[str, Any]:
        """List all suppliers"""
        params = {'page': page, 'page_size': page_size}
        if search:
            params['search'] = search
        return self.client.get('suppliers/', params=params)
    
    def get(self, supplier_id: str) -> Dict[str, Any]:
        """Get a specific supplier by ID"""
        return self.client.get(f'suppliers/{supplier_id}/')
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new supplier"""
        return self.client.post('suppliers/', json=data)
    
    def update(self, supplier_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing supplier"""
        return self.client.patch(f'suppliers/{supplier_id}/', json=data)
    
    def delete(self, supplier_id: str) -> Dict[str, Any]:
        """Delete a supplier"""
        return self.client.delete(f'suppliers/{supplier_id}/')
