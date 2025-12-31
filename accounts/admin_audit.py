"""
Enhanced admin interface for audit logs with search and export.
"""
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from accounts.models import AuditLog, APIRequestLog
import csv
from datetime import datetime


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Enhanced admin for AuditLog with search and export."""
    
    list_display = ['timestamp', 'user_link', 'action', 'model_name', 'tenant_link', 'ip_address']
    list_filter = ['action', 'model_name', 'timestamp', 'tenant']
    search_fields = ['user__username', 'user__email', 'model_name', 'object_id', 'ip_address']
    readonly_fields = ['timestamp', 'user', 'action', 'model_name', 'object_id', 'changes', 'ip_address', 'user_agent', 'tenant']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    list_per_page = 50
    
    actions = ['export_as_csv']
    
    def user_link(self, obj):
        """Display user as clickable link."""
        if obj.user:
            return format_html(
                '<a href="/admin/auth/user/{}/change/">{}</a>',
                obj.user.id,
                obj.user.username
            )
        return '-'
    user_link.short_description = 'User'
    
    def tenant_link(self, obj):
        """Display tenant as clickable link."""
        if obj.tenant:
            return format_html(
                '<a href="/admin/accounts/tenant/{}/change/">{}</a>',
                obj.tenant.id,
                obj.tenant.name
            )
        return '-'
    tenant_link.short_description = 'Tenant'
    
    def export_as_csv(self, request, queryset):
        """Export selected audit logs as CSV."""
        meta = self.model._meta
        field_names = ['timestamp', 'user', 'action', 'model_name', 'object_id', 'tenant', 'ip_address']
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        writer = csv.writer(response)
        writer.writerow(field_names)
        
        for obj in queryset:
            row = [
                obj.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                obj.user.username if obj.user else '',
                obj.action,
                obj.model_name,
                obj.object_id,
                obj.tenant.name if obj.tenant else '',
                obj.ip_address or '',
            ]
            writer.writerow(row)
        
        return response
    export_as_csv.short_description = 'Export selected as CSV'


@admin.register(APIRequestLog)
class APIRequestLogAdmin(admin.ModelAdmin):
    """Enhanced admin for APIRequestLog with search and filtering."""
    
    list_display = ['timestamp', 'user_link', 'method', 'endpoint', 'status_code', 'response_time_display', 'tenant_link']
    list_filter = ['method', 'status_code', 'timestamp', 'tenant']
    search_fields = ['endpoint', 'user__username', 'ip_address']
    readonly_fields = ['timestamp', 'tenant', 'user', 'endpoint', 'method', 'ip_address', 'user_agent', 'request_body', 'response_body', 'status_code', 'response_time_ms']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    list_per_page = 50
    
    actions = ['export_as_csv']
    
    def user_link(self, obj):
        """Display user as clickable link."""
        if obj.user:
            return format_html(
                '<a href="/admin/auth/user/{}/change/">{}</a>',
                obj.user.id,
                obj.user.username
            )
        return '-'
    user_link.short_description = 'User'
    
    def tenant_link(self, obj):
        """Display tenant as clickable link."""
        if obj.tenant:
            return format_html(
                '<a href="/admin/accounts/tenant/{}/change/">{}</a>',
                obj.tenant.id,
                obj.tenant.name
            )
        return '-'
    tenant_link.short_description = 'Tenant'
    
    def response_time_display(self, obj):
        """Display response time with color coding."""
        if obj.response_time_ms is None:
            return '-'
        
        # Color code based on response time
        if obj.response_time_ms < 100:
            color = 'green'
        elif obj.response_time_ms < 500:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {};">{} ms</span>',
            color,
            obj.response_time_ms
        )
    response_time_display.short_description = 'Response Time'
    
    def export_as_csv(self, request, queryset):
        """Export selected API logs as CSV."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=api_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        writer = csv.writer(response)
        writer.writerow(['Timestamp', 'User', 'Method', 'Endpoint', 'Status Code', 'Response Time (ms)', 'IP Address', 'Tenant'])
        
        for obj in queryset:
            row = [
                obj.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                obj.user.username if obj.user else '',
                obj.method,
                obj.endpoint,
                obj.status_code or '',
                obj.response_time_ms or '',
                obj.ip_address or '',
                obj.tenant.name if obj.tenant else '',
            ]
            writer.writerow(row)
        
        return response
    export_as_csv.short_description = 'Export selected as CSV'
