import json
from django.core.serializers.json import DjangoJSONEncoder
from accounts.models import ActivityLog

class AuditService:
    @staticmethod
    def get_field_diff(old_instance, new_instance):
        """
        Compares two instances of a model and returns a dictionary of changes.
        """
        changes = {}
        if not old_instance:
            return changes

        # Get all field names
        fields = [f.name for f in new_instance._meta.fields]
        
        # Exclude internal fields
        exclude = ['updated_at', 'created_at']
        
        for field in fields:
            if field in exclude:
                continue
                
            old_val = getattr(old_instance, field)
            new_val = getattr(new_instance, field)
            
            if old_val != new_val:
                changes[field] = {
                    'old': str(old_val),
                    'new': str(new_val)
                }
        
        return changes

    @staticmethod
    def log_action(request, action_type, description, target_model=None, target_object_id=None, changes=None):
        """
        Creates an ActivityLog entry.
        """
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile:
            return None
            
        return ActivityLog.objects.create(
            tenant=user_profile.tenant,
            actor=user_profile,
            action_type=action_type,
            description=description,
            target_model=target_model or '',
            target_object_id=str(target_object_id) if target_object_id else '',
            changes=changes,
            ip_address=request.META.get('REMOTE_ADDR')
        )
