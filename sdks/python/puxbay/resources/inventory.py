"""
Inventory resource client
"""

from typing import Dict, Any, Optional


class Inventory:
    """Client for inventory-related API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def get_stock_levels(self, branch_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current stock levels for all products
        
        Args:
            branch_id: Filter by specific branch (optional)
        
        Returns:
            List of products with current stock quantities
        """
        params = {}
        if branch_id:
            params['branch'] = branch_id
        return self.client.get('inventory/stock-levels/', params=params)
    
    def get_low_stock(self, threshold: int = 10) -> Dict[str, Any]:
        """
        Get products with low stock
        
        Args:
            threshold: Stock quantity threshold (default: 10)
        
        Returns:
            List of products below the threshold
        """
        return self.client.get('inventory/low-stock/', params={'threshold': threshold})
    
    def create_transfer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a stock transfer between branches
        
        Args:
            data: Transfer data (from_branch, to_branch, items)
        
        Returns:
            Created transfer record
        
        Example:
            >>> transfer_data = {
            ...     "from_branch": "branch-uuid-1",
            ...     "to_branch": "branch-uuid-2",
            ...     "items": [
            ...         {"product": "product-uuid", "quantity": 10}
            ...     ]
            ... }
            >>> transfer = client.inventory.create_transfer(transfer_data)
        """
        return self.client.post('stock-transfers/', json=data)
    
    def list_transfers(self, page: int = 1, status: Optional[str] = None) -> Dict[str, Any]:
        """
        List stock transfers
        
        Args:
            page: Page number (default: 1)
            status: Filter by status (pending, completed, cancelled)
        
        Returns:
            Paginated list of transfers
        """
        params = {'page': page}
        if status:
            params['status'] = status
        return self.client.get('stock-transfers/', params=params)
    
    def create_stocktake(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a stocktake (physical inventory count)
        
        Args:
            data: Stocktake data (branch, items with counted quantities)
        
        Returns:
            Created stocktake record
        """
        return self.client.post('stocktakes/', json=data)
    
    def list_stocktakes(self, page: int = 1) -> Dict[str, Any]:
        """
        List stocktakes
        
        Args:
            page: Page number (default: 1)
        
        Returns:
            Paginated list of stocktakes
        """
        return self.client.get('stocktakes/', params={'page': page})
