import pytest
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

# The same validator used in the model
subdomain_validator = RegexValidator(
    regex='^[a-z]+$',
    message='Subdomain must only contain lowercase letters, with no numbers, spaces, or special characters.'
)

class TestSubdomainValidation:
    """Test the subdomain validation logic using the RegexValidator directly."""

    def test_valid_subdomains(self):
        """Test subdomains that should pass validation."""
        valid_subdomains = ['mystore', 'puxbay']
        for subdomain in valid_subdomains:
            # Should not raise any error
            subdomain_validator(subdomain)

    def test_invalid_subdomains_numbers(self):
        """Test that numbers are rejected."""
        invalid_subdomains = ['store123', '123store', 's123']
        for subdomain in invalid_subdomains:
            with pytest.raises(ValidationError) as excinfo:
                subdomain_validator(subdomain)
            assert 'Subdomain must only contain lowercase letters' in str(excinfo.value)

    def test_invalid_subdomains_uppercase(self):
        """Test that uppercase letters are rejected."""
        invalid_subdomains = ['MyStore', 'PUXBAY', 'storeA']
        for subdomain in invalid_subdomains:
            with pytest.raises(ValidationError) as excinfo:
                subdomain_validator(subdomain)
            assert 'Subdomain must only contain lowercase letters' in str(excinfo.value)

    def test_invalid_subdomains_spaces(self):
        """Test that spaces are rejected."""
        with pytest.raises(ValidationError) as excinfo:
            subdomain_validator("my store")
        assert 'Subdomain must only contain lowercase letters' in str(excinfo.value)

    def test_invalid_subdomains_special_characters(self):
        """Test that special characters are rejected."""
        invalid_subdomains = ['my-store', 'my_store', 'store!', 'store.com']
        for subdomain in invalid_subdomains:
            with pytest.raises(ValidationError) as excinfo:
                subdomain_validator(subdomain)
            assert 'Subdomain must only contain lowercase letters' in str(excinfo.value)
