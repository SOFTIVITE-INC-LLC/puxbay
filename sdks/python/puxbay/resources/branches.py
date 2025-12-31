"""
Branches resource client
"""

from typing import Dict, Any, Optional


class Branches:
    """Client for branch-related API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def list(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """List all branches"""
        return self.client.get('branches/', params={'page': page, 'page_size': page_size})
    
    def get(self, branch_id: str) -> Dict[str, Any]:
        """Get a specific branch by ID"""
        return self.client.get(f'branches/{branch_id}/')
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new branch"""
        return self.client.post('branches/', json=data)
    
    def update(self, branch_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing branch"""
        return self.client.patch(f'branches/{branch_id}/', json=data)
    
    def delete(self, branch_id: str) -> Dict[str, Any]:
        """Delete a branch"""
        return self.client.delete(f'branches/{branch_id}/')
