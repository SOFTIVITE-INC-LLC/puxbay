"""
Orders resource client
"""

from typing import List, Dict, Any, Optional


class Orders:
    """Client for order-related API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all orders
        
        Args:
            page: Page number (default: 1)
            page_size: Number of items per page (default: 20)
            status: Filter by order status (pending, completed, cancelled)
            customer_id: Filter by customer ID
        
        Returns:
            Paginated list of orders
        """
        params = {'page': page, 'page_size': page_size}
        if status:
            params['status'] = status
        if customer_id:
            params['customer'] = customer_id
        return self.client.get('orders/', params=params)
    
    def get(self, order_id: str) -> Dict[str, Any]:
        """
        Get a specific order by ID
        
        Args:
            order_id: Order UUID
        
        Returns:
            Order details with line items
        """
        return self.client.get(f'orders/{order_id}/')
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new order
        
        Args:
            data: Order data including customer, items, payment method, etc.
        
        Returns:
            Created order
        
        Example:
            >>> order_data = {
            ...     "customer": "customer-uuid",
            ...     "items": [
            ...         {"product": "product-uuid", "quantity": 2, "price": 29.99}
            ...     ],
            ...     "payment_method": "cash",
            ...     "status": "completed"
            ... }
            >>> order = client.orders.create(order_data)
        """
        return self.client.post('orders/', json=data)
    
    def update(self, order_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing order
        
        Args:
            order_id: Order UUID
            data: Updated order data
        
        Returns:
            Updated order
        """
        return self.client.patch(f'orders/{order_id}/', json=data)
    
    def cancel(self, order_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel an order
        
        Args:
            order_id: Order UUID
            reason: Cancellation reason
        
        Returns:
            Cancelled order
        """
        data = {'status': 'cancelled'}
        if reason:
            data['cancellation_reason'] = reason
        return self.client.patch(f'orders/{order_id}/', json=data)
