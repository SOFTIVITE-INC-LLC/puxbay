"""
Puxbay Python SDK

Official Python client library for the Puxbay POS API.
"""

__version__ = "1.0.0"

from .client import Puxbay
from .exceptions import (
    PuxbayError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    ServerError
)

__all__ = [
    "Puxbay",
    "PuxbayError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "NotFoundError",
    "ServerError"
]
