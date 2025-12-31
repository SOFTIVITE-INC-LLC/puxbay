"""
Staff resource client
"""

from typing import Dict, Any, Optional


class Staff:
    """Client for staff-related API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def list(self, page: int = 1, page_size: int = 20, role: Optional[str] = None) -> Dict[str, Any]:
        """List all staff members"""
        params = {'page': page, 'page_size': page_size}
        if role:
            params['role'] = role
        return self.client.get('staff/', params=params)
    
    def get(self, staff_id: str) -> Dict[str, Any]:
        """Get a specific staff member by ID"""
        return self.client.get(f'staff/{staff_id}/')
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new staff member"""
        return self.client.post('staff/', json=data)
    
    def update(self, staff_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing staff member"""
        return self.client.patch(f'staff/{staff_id}/', json=data)
    
    def delete(self, staff_id: str) -> Dict[str, Any]:
        """Delete a staff member"""
        return self.client.delete(f'staff/{staff_id}/')
