"""
Expenses resource client
"""

from typing import Dict, Any, Optional


class Expenses:
    """Client for expense-related API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def list(self, page: int = 1, page_size: int = 20, category: Optional[str] = None) -> Dict[str, Any]:
        """List all expenses"""
        params = {'page': page, 'page_size': page_size}
        if category:
            params['category'] = category
        return self.client.get('expenses/', params=params)
    
    def get(self, expense_id: str) -> Dict[str, Any]:
        """Get a specific expense by ID"""
        return self.client.get(f'expenses/{expense_id}/')
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new expense"""
        return self.client.post('expenses/', json=data)
    
    def update(self, expense_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing expense"""
        return self.client.patch(f'expenses/{expense_id}/', json=data)
    
    def delete(self, expense_id: str) -> Dict[str, Any]:
        """Delete an expense"""
        return self.client.delete(f'expenses/{expense_id}/')
    
    def list_categories(self) -> Dict[str, Any]:
        """List all expense categories"""
        return self.client.get('expense-categories/')
