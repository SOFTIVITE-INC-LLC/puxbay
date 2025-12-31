from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .utils import log_activity
from .models import UserProfile

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # Ensure profile exists (might be admin user without profile)
    if hasattr(user, 'profile'):
        log_activity(request, 'login', f"User {user.username} logged in.")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user and hasattr(user, 'profile'):
        log_activity(request, 'logout', f"User {user.username} logged out.")

# Auto-generate unique identifiers
from django.db.models.signals import pre_save
from .models import Branch

@receiver(pre_save, sender=Branch)
def auto_generate_branch_id(sender, instance, **kwargs):
    """
    Auto-generate unique_id for Branch if not already set.
    """
    if not instance.unique_id and instance.tenant:
        from utils.identifier_generator import generate_branch_id
        instance.unique_id = generate_branch_id(instance.tenant)
