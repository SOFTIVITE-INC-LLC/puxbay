"""
Security validators for production deployment.

Validates that critical security settings are properly configured
before allowing the application to start in production mode.
"""
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


class SecurityValidator:
    """Validates security configuration at startup."""
    
    INSECURE_SECRETS = [
        'django-insecure-change-me-in-production',
        'change-me-in-production',
        'your-super-secret-key-generate-a-new-one',
        'your-fernet-key-here',
        'your-webhook-secret-change-in-production',
    ]
    
    @classmethod
    def validate_all(cls):
        """Run all security validations."""
        if not settings.DEBUG:
            cls.validate_secret_key()
            cls.validate_fernet_key()
            cls.validate_allowed_hosts()
            cls.validate_database()
    
    @classmethod
    def validate_secret_key(cls):
        """Ensure SECRET_KEY is not using default value."""
        secret_key = settings.SECRET_KEY
        
        if not secret_key:
            raise ImproperlyConfigured(
                "SECRET_KEY must be set in production. "
                "Generate a secure key and set it in your environment variables."
            )
        
        if secret_key in cls.INSECURE_SECRETS:
            raise ImproperlyConfigured(
                f"SECRET_KEY is using an insecure default value: '{secret_key}'. "
                "Generate a secure key using: "
                "python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
            )
        
        if len(secret_key) < 50:
            raise ImproperlyConfigured(
                f"SECRET_KEY is too short ({len(secret_key)} characters). "
                "It should be at least 50 characters long."
            )
    
    @classmethod
    def validate_fernet_key(cls):
        """Ensure FERNET_KEY is not using default value."""
        try:
            fernet_key = settings.FERNET_KEY.decode() if isinstance(settings.FERNET_KEY, bytes) else settings.FERNET_KEY
        except AttributeError:
            raise ImproperlyConfigured(
                "FERNET_KEY is not properly configured. "
                "Generate a key using: "
                "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        
        if fernet_key in cls.INSECURE_SECRETS:
            raise ImproperlyConfigured(
                "FERNET_KEY is using an insecure default value. "
                "Generate a secure key using: "
                "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
    
    @classmethod
    def validate_allowed_hosts(cls):
        """Ensure ALLOWED_HOSTS is properly configured."""
        allowed_hosts = settings.ALLOWED_HOSTS
        
        if not allowed_hosts or allowed_hosts == ['*']:
            raise ImproperlyConfigured(
                "ALLOWED_HOSTS must be explicitly set in production. "
                "Do not use ['*'] as it's a security risk."
            )
    
    @classmethod
    def validate_database(cls):
        """Ensure database is not using SQLite in production."""
        default_db = settings.DATABASES.get('default', {})
        engine = default_db.get('ENGINE', '')
        
        if 'sqlite' in engine.lower():
            raise ImproperlyConfigured(
                "SQLite database is not recommended for production. "
                "Please use PostgreSQL or another production-grade database."
            )
