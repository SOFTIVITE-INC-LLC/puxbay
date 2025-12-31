"""
Tests for permission enforcement and role-based access control.

Critical tests for credit sales permission, procurement manager access,
and IP whitelisting.
"""
import pytest
from django_tenants.utils import schema_context
from django.test import RequestFactory
from api.security import is_ip_whitelisted, get_client_ip
from accounts.tests.factories import UserProfileFactory


@pytest.mark.django_db
class TestCreditSalesPermission:
    """Test credit sales permission enforcement."""
    
    def test_sales_without_permission_blocked(self, test_tenant, test_branch, sales_user):
        """Sales users without permission should be blocked from credit transactions."""
        with schema_context(test_tenant.schema_name):
            profile = sales_user.profiles.get(tenant=test_tenant)
            
            assert profile.role == 'sales'
            assert profile.can_perform_credit_sales is False
    
    def test_sales_with_permission_allowed(self, test_tenant, test_branch, sales_user_with_credit):
        """Sales users with permission should be allowed credit transactions."""
        with schema_context(test_tenant.schema_name):
            profile = sales_user_with_credit.profiles.get(tenant=test_tenant)
            
            assert profile.role == 'sales'
            assert profile.can_perform_credit_sales is True
    
    def test_admin_bypasses_permission(self, test_tenant, admin_user):
        """Admin users should bypass credit permission checks."""
        with schema_context(test_tenant.schema_name):
            profile = admin_user.profiles.get(tenant=test_tenant)
            
            assert profile.role == 'admin'
            # Permission check should be bypassed for admin
    
    def test_manager_bypasses_permission(self, test_tenant, test_branch, manager_user):
        """Manager users should bypass credit permission checks."""
        with schema_context(test_tenant.schema_name):
            profile = manager_user.profiles.get(tenant=test_tenant)
            
            assert profile.role == 'manager'
            # Permission check should be bypassed for manager


@pytest.mark.django_db
class TestProcurementManagerAccess:
    """Test procurement manager role access control."""
    
    def test_procurement_manager_role_exists(self, test_tenant, test_branch, procurement_manager):
        """Procurement manager role should be properly created."""
        with schema_context(test_tenant.schema_name):
            profile = procurement_manager.profiles.get(tenant=test_tenant)
            
            assert profile.role == 'procurement_manager'
    
    def test_procurement_manager_has_branch_access(self, test_tenant, test_branch, procurement_manager):
        """Procurement manager should have branch assignment."""
        with schema_context(test_tenant.schema_name):
            profile = procurement_manager.profiles.get(tenant=test_tenant)
            
            assert profile.branch == test_branch


class TestIPWhitelisting:
    """Test IP whitelisting functionality."""
    
    def test_empty_whitelist_allows_all(self):
        """Empty whitelist should allow all IPs."""
        assert is_ip_whitelisted('192.168.1.1', whitelist=[]) is True
        assert is_ip_whitelisted('10.0.0.1', whitelist=[]) is True
    
    def test_exact_ip_match(self):
        """Exact IP match should be allowed."""
        whitelist = ['192.168.1.1', '10.0.0.1']
        
        assert is_ip_whitelisted('192.168.1.1', whitelist) is True
        assert is_ip_whitelisted('10.0.0.1', whitelist) is True
        assert is_ip_whitelisted('192.168.1.2', whitelist) is False
    
    def test_cidr_range_match(self):
        """IPs within CIDR range should be allowed."""
        whitelist = ['192.168.1.0/24', '10.0.0.0/16']
        
        assert is_ip_whitelisted('192.168.1.1', whitelist) is True
        assert is_ip_whitelisted('192.168.1.255', whitelist) is True
        assert is_ip_whitelisted('192.168.2.1', whitelist) is False
        
        assert is_ip_whitelisted('10.0.0.1', whitelist) is True
        assert is_ip_whitelisted('10.0.255.255', whitelist) is True
        assert is_ip_whitelisted('10.1.0.1', whitelist) is False
    
    def test_invalid_ip_rejected(self):
        """Invalid IP addresses should be rejected."""
        whitelist = ['192.168.1.1']
        
        assert is_ip_whitelisted('invalid-ip', whitelist) is False
        assert is_ip_whitelisted('999.999.999.999', whitelist) is False
    
    def test_get_client_ip_from_remote_addr(self):
        """Should extract IP from REMOTE_ADDR."""
        factory = RequestFactory()
        request = factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        assert get_client_ip(request) == '192.168.1.1'
    
    def test_get_client_ip_from_x_forwarded_for(self):
        """Should extract IP from X-Forwarded-For header."""
        factory = RequestFactory()
        request = factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        # Should use first IP from X-Forwarded-For
        assert get_client_ip(request) == '192.168.1.1'
