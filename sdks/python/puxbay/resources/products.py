"""
Products resource client
"""

from typing import List, Dict, Any, Optional


class Products:
    """Client for product-related API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def list(self, page: int = 1, page_size: int = 20, search: Optional[str] = None) -> Dict[str, Any]:
        """
        List all products
        
        Args:
            page: Page number (default: 1)
            page_size: Number of items per page (default: 20)
            search: Search query for product name or SKU
        
        Returns:
            Paginated list of products
        """
        params = {'page': page, 'page_size': page_size}
        if search:
            params['search'] = search
        return self.client.get('products/', params=params)
    
    def get(self, product_id: str) -> Dict[str, Any]:
        """
        Get a specific product by ID
        
        Args:
            product_id: Product UUID
        
        Returns:
            Product details
        """
        return self.client.get(f'products/{product_id}/')
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new product
        
        Args:
            data: Product data (name, sku, price, category, etc.)
        
        Returns:
            Created product
        """
        return self.client.post('products/', json=data)
    
    def update(self, product_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing product
        
        Args:
            product_id: Product UUID
            data: Updated product data
        
        Returns:
            Updated product
        """
        return self.client.patch(f'products/{product_id}/', json=data)
    
    def delete(self, product_id: str) -> Dict[str, Any]:
        """
        Delete a product
        
        Args:
            product_id: Product UUID
        
        Returns:
            Deletion confirmation
        """
        return self.client.delete(f'products/{product_id}/')
    
    def adjust_stock(self, product_id: str, quantity: int, reason: str = "manual_adjustment") -> Dict[str, Any]:
        """
        Adjust product stock quantity
        
        Args:
            product_id: Product UUID
            quantity: Quantity to add (positive) or remove (negative)
            reason: Reason for adjustment
        
        Returns:
            Updated product with new stock quantity
        """
        return self.client.post(f'products/{product_id}/adjust_stock/', json={
            'quantity': quantity,
            'reason': reason
        })
