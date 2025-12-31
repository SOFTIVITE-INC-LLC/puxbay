"""
Tests for API security features.

Tests for rate limiting, webhook signature validation, and audit logging.
"""
import pytest
import time
from django.test import RequestFactory, Client
from django.core.cache import cache
from api.security import generate_webhook_signature, verify_webhook_signature


class TestWebhookSignatures:
    """Test webhook signature generation and validation."""
    
    def test_signature_generation(self):
        """Should generate consistent HMAC-SHA256 signatures."""
        payload = b'{"event": "test", "data": "value"}'
        secret = 'test-secret-key'
        
        signature1 = generate_webhook_signature(payload, secret)
        signature2 = generate_webhook_signature(payload, secret)
        
        # Same payload and secret should produce same signature
        assert signature1 == signature2
        assert len(signature1) == 64  # SHA256 hex is 64 chars
    
    def test_signature_validation_success(self):
        """Valid signature should pass verification."""
        payload = b'{"event": "test"}'
        secret = 'test-secret'
        
        signature = generate_webhook_signature(payload, secret)
        
        assert verify_webhook_signature(payload, signature, secret) is True
    
    def test_signature_validation_failure(self):
        """Invalid signature should fail verification."""
        payload = b'{"event": "test"}'
        secret = 'test-secret'
        
        signature = generate_webhook_signature(payload, secret)
        
        # Wrong secret
        assert verify_webhook_signature(payload, signature, 'wrong-secret') is False
        
        # Wrong payload
        assert verify_webhook_signature(b'{"event": "different"}', signature, secret) is False
        
        # Wrong signature
        assert verify_webhook_signature(payload, 'invalid-signature', secret) is False
    
    def test_signature_different_for_different_payloads(self):
        """Different payloads should produce different signatures."""
        secret = 'test-secret'
        
        sig1 = generate_webhook_signature(b'{"event": "test1"}', secret)
        sig2 = generate_webhook_signature(b'{"event": "test2"}', secret)
        
        assert sig1 != sig2


@pytest.mark.django_db
class TestAPIAuditLogging:
    """Test API request audit logging."""
    
    def test_api_requests_are_logged(self, admin_user):
        """API requests should be logged to database."""
        from accounts.models import APIRequestLog
        
        client = Client()
        client.force_login(admin_user)
        
        # Clear existing logs
        APIRequestLog.objects.all().delete()
        
        # Make API request
        response = client.get('/api/v1/health/')
        
        # Note: Health endpoint might be excluded, use a different endpoint
        # This is a placeholder - adjust based on actual API endpoints
        
        # Verify log was created (if not excluded)
        # logs = APIRequestLog.objects.all()
        # assert logs.count() > 0
    
    def test_audit_log_captures_metadata(self):
        """Audit logs should capture request metadata."""
        from accounts.models import APIRequestLog
        
        # This would need to be tested with actual middleware
        # Placeholder for structure verification
        pass


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def setUp(self):
        """Clear cache before each test."""
        cache.clear()
    
    def test_rate_limit_allows_within_limit(self):
        """Requests within rate limit should be allowed."""
        # This would require testing with actual rate limit decorator
        # Placeholder for integration test
        pass
    
    def test_rate_limit_blocks_over_limit(self):
        """Requests exceeding rate limit should be blocked."""
        # This would require testing with actual rate limit decorator
        # Placeholder for integration test
        pass
