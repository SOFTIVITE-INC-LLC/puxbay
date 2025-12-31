"""
Custom exceptions for the Puxbay SDK
"""

class PuxbayError(Exception):
    """Base exception for all Puxbay SDK errors"""
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class AuthenticationError(PuxbayError):
    """Raised when API key authentication fails"""
    pass


class RateLimitError(PuxbayError):
    """Raised when API rate limit is exceeded"""
    pass


class ValidationError(PuxbayError):
    """Raised when request validation fails"""
    pass


class NotFoundError(PuxbayError):
    """Raised when a resource is not found"""
    pass


class ServerError(PuxbayError):
    """Raised when the server returns a 5xx error"""
    pass
