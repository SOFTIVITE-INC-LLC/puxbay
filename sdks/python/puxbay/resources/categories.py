"""
Categories resource client
"""

from typing import Dict, Any, Optional


class Categories:
    """Client for category-related API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def list(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """List all categories"""
        return self.client.get('categories/', params={'page': page, 'page_size': page_size})
    
    def get(self, category_id: str) -> Dict[str, Any]:
        """Get a specific category by ID"""
        return self.client.get(f'categories/{category_id}/')
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new category"""
        return self.client.post('categories/', json=data)
    
    def update(self, category_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing category"""
        return self.client.patch(f'categories/{category_id}/', json=data)
    
    def delete(self, category_id: str) -> Dict[str, Any]:
        """Delete a category"""
        return self.client.delete(f'categories/{category_id}/')
