from rest_framework import serializers
from django.contrib.auth.models import User
from accounts.models import Tenant, Branch, UserProfile, WebhookEndpoint, WebhookEvent

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'subdomain', 'created_on']

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'unique_id', 'address', 'phone', 'branch_type']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tenant = TenantSerializer(read_only=True)
    branch = BranchSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'tenant', 'branch', 'role', 'is_2fa_enabled']

class WebhookEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint
        fields = ['id', 'url', 'secret', 'events', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class WebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = ['id', 'event_type', 'payload', 'status_code', 'response_body', 'error_message', 'timestamp']
        read_only_fields = ['id', 'timestamp']
