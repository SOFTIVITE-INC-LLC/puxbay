"""
Main Puxbay client class with performance optimizations
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any
import time
from functools import lru_cache
from .exceptions import (
    PuxbayError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    ServerError
)
from .resources.products import Products
from .resources.orders import Orders
from .resources.customers import Customers
from .resources.inventory import Inventory
from .resources.reports import Reports
from .resources.categories import Categories
from .resources.suppliers import Suppliers
from .resources.purchase_orders import PurchaseOrders
from .resources.gift_cards import GiftCards
from .resources.expenses import Expenses
from .resources.branches import Branches
from .resources.staff import Staff
from .resources.webhooks import Webhooks


class Puxbay:
    """
    Main client for interacting with the Puxbay API with performance optimizations.
    
    Features:
    - Connection pooling for better performance
    - Automatic retry with exponential backoff
    - Request timeout configuration
    - Session reuse for connection persistence
    
    Args:
        api_key: Your Puxbay API key (starts with 'pb_')
        base_url: API base URL (default: https://api.puxbay.com/api/v1)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retry attempts (default: 3)
        pool_connections: Number of connection pool connections (default: 10)
        pool_maxsize: Maximum size of the connection pool (default: 20)
    
    Example:
        >>> from puxbay import Puxbay
        >>> client = Puxbay(
        ...     api_key="pb_your_api_key_here",
        ...     max_retries=5,
        ...     pool_connections=20
        ... )
        >>> products = client.products.list()
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.puxbay.com/api/v1",
        timeout: int = 30,
        max_retries: int = 3,
        pool_connections: int = 10,
        pool_maxsize: int = 20
    ):
        if not api_key or not api_key.startswith('pb_'):
            raise ValueError("Invalid API key format. Must start with 'pb_'")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Create session with connection pooling
        self.session = requests.Session()
        
        # Configure retry strategy with exponential backoff
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,  # Wait 1s, 2s, 4s, 8s between retries
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST", "PATCH"]
        )
        
        # Configure HTTP adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            pool_block=False
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'puxbay-python/1.0.0',
            'Accept-Encoding': 'gzip, deflate',  # Enable compression
            'Connection': 'keep-alive'  # Keep connections alive
        })
        
        # Initialize resource clients
        self.products = Products(self)
        self.orders = Orders(self)
        self.customers = Customers(self)
        self.inventory = Inventory(self)
        self.reports = Reports(self)
        self.categories = Categories(self)
        self.suppliers = Suppliers(self)
        self.purchase_orders = PurchaseOrders(self)
        self.gift_cards = GiftCards(self)
        self.expenses = Expenses(self)
        self.branches = Branches(self)
        self.staff = Staff(self)
        self.webhooks = Webhooks(self)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json: JSON request body
        
        Returns:
            Response data as dictionary
        
        Raises:
            AuthenticationError: Invalid or missing API key
            RateLimitError: Rate limit exceeded
            ValidationError: Request validation failed
            NotFoundError: Resource not found
            ServerError: Server error occurred
            PuxbayError: Other API errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=self.timeout
            )
            
            # Handle different status codes
            if response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed. Check your API key.",
                    status_code=401,
                    response=response
                )
            elif response.status_code == 429:
                raise RateLimitError(
                    "Rate limit exceeded. Please try again later.",
                    status_code=429,
                    response=response
                )
            elif response.status_code == 400:
                raise ValidationError(
                    response.json().get('detail', 'Validation error'),
                    status_code=400,
                    response=response
                )
            elif response.status_code == 404:
                raise NotFoundError(
                    "Resource not found",
                    status_code=404,
                    response=response
                )
            elif 500 <= response.status_code < 600:
                raise ServerError(
                    f"Server error: {response.status_code}",
                    status_code=response.status_code,
                    response=response
                )
            
            response.raise_for_status()
            
            # Return JSON response if available
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.Timeout:
            raise PuxbayError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.RequestException as e:
            raise PuxbayError(f"Request failed: {str(e)}")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request"""
        return self._request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request"""
        return self._request('POST', endpoint, json=json)
    
    def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request"""
        return self._request('PUT', endpoint, json=json)
    
    def patch(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PATCH request"""
        return self._request('PATCH', endpoint, json=json)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request"""
        return self._request('DELETE', endpoint)
    
    def close(self):
        """Close the session and release resources"""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources"""
        self.close()
