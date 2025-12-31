"""
Gift Cards resource client
"""

from typing import Dict, Any, Optional


class GiftCards:
    """Client for gift card-related API endpoints"""
    
    def __init__(self, client):
        self.client = client
    
    def list(self, page: int = 1, page_size: int = 20, status: Optional[str] = None) -> Dict[str, Any]:
        """List all gift cards"""
        params = {'page': page, 'page_size': page_size}
        if status:
            params['status'] = status
        return self.client.get('gift-cards/', params=params)
    
    def get(self, card_id: str) -> Dict[str, Any]:
        """Get a specific gift card by ID"""
        return self.client.get(f'gift-cards/{card_id}/')
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new gift card"""
        return self.client.post('gift-cards/', json=data)
    
    def redeem(self, card_id: str, amount: float) -> Dict[str, Any]:
        """Redeem a gift card"""
        return self.client.post(f'gift-cards/{card_id}/redeem/', json={'amount': amount})
    
    def check_balance(self, card_code: str) -> Dict[str, Any]:
        """Check gift card balance by code"""
        return self.client.get(f'gift-cards/check-balance/', params={'code': card_code})
