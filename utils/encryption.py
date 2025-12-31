from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings
import base64

class EncryptedTextField(models.TextField):
    """
    A custom field that encrypts data before saving to DB and decrypts on retrieval.
    Usage:
        secret_data = EncryptedTextField()
    """
    description = "Encrypted Text Field"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_fernet(self):
        key = getattr(settings, 'FERNET_KEY', None)
        if not key:
            raise ValueError("FERNET_KEY is not set in settings.")
        return Fernet(key)

    def get_prep_value(self, value):
        """Encrypt the value before saving to the database."""
        if value is None:
            return None
        if not isinstance(value, str):
            value = str(value)
        
        fernet = self.get_fernet()
        encrypted_value = fernet.encrypt(value.encode('utf-8'))
        return encrypted_value.decode('utf-8')

    def from_db_value(self, value, expression, connection):
        """Decrypt the value when retrieving from the database."""
        if value is None:
            return None
        
        try:
            fernet = self.get_fernet()
            decrypted_value = fernet.decrypt(value.encode('utf-8'))
            return decrypted_value.decode('utf-8')
        except Exception:
            # If decryption fails (e.g. key changed or bad data), return raw or empty
            return value

    def to_python(self, value):
        """Ensure the value is in python format (decrypted handled by from_db_value normally, but for forms/serializers)."""
        # If accessing directly on model instance that was just assigned, it might be plain text.
        # If coming from DB, it's already decrypted by from_db_value.
        return value
