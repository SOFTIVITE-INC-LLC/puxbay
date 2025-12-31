"""
Reports resource client
"""

from typing import Dict, Any, Optional
from datetime import date


class Reports:
    """Client for reports and analytics API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def sales_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        branch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get sales summary report
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            branch_id: Filter by specific branch
        
        Returns:
            Sales summary with totals, averages, and trends
        """
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if branch_id:
            params['branch'] = branch_id
        return self.client.get('reports/sales-summary/', params=params)
    
    def product_performance(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get product performance report
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            limit: Number of top products to return
        
        Returns:
            List of products sorted by sales performance
        """
        params = {'limit': limit}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self.client.get('reports/product-performance/', params=params)
    
    def customer_analytics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get customer analytics report
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
        
        Returns:
            Customer metrics including new customers, retention, lifetime value
        """
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self.client.get('reports/customer-analytics/', params=params)
    
    def inventory_valuation(self, branch_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get inventory valuation report
        
        Args:
            branch_id: Filter by specific branch
        
        Returns:
            Total inventory value and breakdown by category
        """
        params = {}
        if branch_id:
            params['branch'] = branch_id
        return self.client.get('reports/inventory-valuation/', params=params)
    
    def profit_loss(
        self,
        start_date: str,
        end_date: str,
        branch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get profit & loss report
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            branch_id: Filter by specific branch
        
        Returns:
            P&L statement with revenue, costs, and profit
        """
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        if branch_id:
            params['branch'] = branch_id
        return self.client.get('reports/profit-loss/', params=params)
