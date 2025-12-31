"""
Customers resource client
"""

from typing import Dict, Any, Optional


class Customers:
    """Client for customer-related API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def list(self, page: int = 1, page_size: int = 20, search: Optional[str] = None) -> Dict[str, Any]:
        """
        List all customers
        
        Args:
            page: Page number (default: 1)
            page_size: Number of items per page (default: 20)
            search: Search query for customer name, email, or phone
        
        Returns:
            Paginated list of customers
        """
        params = {'page': page, 'page_size': page_size}
        if search:
            params['search'] = search
        return self.client.get('customers/', params=params)
    
    def get(self, customer_id: str) -> Dict[str, Any]:
        """
        Get a specific customer by ID
        
        Args:
            customer_id: Customer UUID
        
        Returns:
            Customer details with loyalty points and store credit
        """
        return self.client.get(f'customers/{customer_id}/')
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new customer
        
        Args:
            data: Customer data (name, email, phone, etc.)
        
        Returns:
            Created customer
        
        Example:
            >>> customer_data = {
            ...     "name": "John Doe",
            ...     "email": "john@example.com",
            ...     "phone": "+1234567890"
            ... }
            >>> customer = client.customers.create(customer_data)
        """
        return self.client.post('customers/', json=data)
    
    def update(self, customer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing customer
        
        Args:
            customer_id: Customer UUID
            data: Updated customer data
        
        Returns:
            Updated customer
        """
        return self.client.patch(f'customers/{customer_id}/', json=data)
    
    def delete(self, customer_id: str) -> Dict[str, Any]:
        """
        Delete a customer
        
        Args:
            customer_id: Customer UUID
        
        Returns:
            Deletion confirmation
        """
        return self.client.delete(f'customers/{customer_id}/')
    
    def add_loyalty_points(self, customer_id: str, points: int, description: str = "") -> Dict[str, Any]:
        """
        Add loyalty points to a customer
        
        Args:
            customer_id: Customer UUID
            points: Number of points to add
            description: Description of the transaction
        
        Returns:
            Updated customer with new loyalty balance
        """
        return self.client.post(f'customers/{customer_id}/add_loyalty_points/', json={
            'points': points,
            'description': description
        })
    
    def add_store_credit(self, customer_id: str, amount: float, description: str = "") -> Dict[str, Any]:
        """
        Add store credit to a customer
        
        Args:
            customer_id: Customer UUID
            amount: Credit amount to add
            description: Description of the transaction
        
        Returns:
            Updated customer with new store credit balance
        """
        return self.client.post(f'customers/{customer_id}/add_store_credit/', json={
            'amount': amount,
            'description': description
        })
