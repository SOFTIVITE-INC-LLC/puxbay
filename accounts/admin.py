from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from unfold.admin import ModelAdmin
from .models import Tenant, Branch, UserProfile, Attendance, ActivityLog, SystemLog, CrossTenantAuditLog, APIKey, SEOSettings

# Import enhanced audit log admins
from .admin_audit import AuditLogAdmin, APIRequestLogAdmin

@admin.register(Tenant)
class TenantAdmin(ModelAdmin):
    list_display = ('name', 'subdomain', 'branches_count', 'products_count', 'orders_count', 'revenue_display', 'created_on', 'admin_link')
    search_fields = ('name', 'subdomain')
    list_filter = ('created_on',)
    
    # Import bulk actions
    from .bulk_actions import bulk_export_tenant_data, bulk_send_notification, bulk_generate_report
    actions = [bulk_export_tenant_data, bulk_send_notification, bulk_generate_report]
    
    def branches_count(self, obj):
        """Display number of active branches"""
        count = obj.branches.count()
        color = 'text-green-600' if count > 0 else 'text-gray-400'
        return format_html('<span class="{}">{}</span>', color, count)
    branches_count.short_description = "Branches"
    
    def products_count(self, obj):
        """Display total products across all branches"""
        from django.db import connection
        try:
            # Switch to tenant schema to query products
            with connection.cursor() as cursor:
                cursor.execute(f"SET search_path TO {obj.schema_name}")
                cursor.execute("SELECT COUNT(*) FROM main_product")
                count = cursor.fetchone()[0]
                cursor.execute("SET search_path TO public")
            
            color = 'text-green-600' if count > 0 else 'text-gray-400'
            return format_html('<span class="{}">{}</span>', color, count)
        except Exception as e:
            return format_html('<span class="text-red-500">Error</span>')
    products_count.short_description = "Products"
    
    def orders_count(self, obj):
        """Display total orders"""
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SET search_path TO {obj.schema_name}")
                cursor.execute("SELECT COUNT(*) FROM main_order")
                count = cursor.fetchone()[0]
                cursor.execute("SET search_path TO public")
            
            color = 'text-green-600' if count > 0 else 'text-gray-400'
            return format_html('<span class="{}">{}</span>', color, count)
        except Exception:
            return format_html('<span class="text-gray-400">-</span>')
    orders_count.short_description = "Orders"
    
    def revenue_display(self, obj):
        """Display total revenue"""
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SET search_path TO {obj.schema_name}")
                cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM main_order WHERE status = 'completed'")
                revenue = cursor.fetchone()[0]
                cursor.execute("SET search_path TO public")
            
            if revenue > 10000:
                color = 'text-green-600 font-semibold'
            elif revenue > 1000:
                color = 'text-blue-600'
            elif revenue > 0:
                color = 'text-yellow-600'
            else:
                color = 'text-gray-400'
            
            return format_html('<span class="${:,.2f}</span>', color, float(revenue))
        except Exception:
            return format_html('<span class="text-gray-400">$0.00</span>')
    revenue_display.short_description = "Revenue"
    
    def admin_link(self, obj):
        domain = obj.domains.first()
        if domain:
            url = f"http://{domain.domain}/admin/"
            return format_html('<a href="{}" target="_blank" class="px-3 py-2 text-white bg-indigo-600 hover:bg-indigo-700 rounded-md text-xs font-bold no-underline">Visit Admin</a>', url)
        return "No Domain"
    admin_link.short_description = "Admin Access"

@admin.register(Branch)
class BranchAdmin(ModelAdmin):
    list_display = ('name', 'tenant', 'branch_type', 'phone', 'created_at', 'print_qr')
    list_filter = ('tenant', 'branch_type', 'created_at')
    search_fields = ('name', 'address', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'print_qr')

    def print_qr(self, obj):
        url = reverse('print_branch_qr', args=[obj.id])
        return format_html('<a href="{}" target="_blank" class="px-3 py-2 text-white bg-indigo-600 hover:bg-indigo-700 rounded-md text-xs font-bold no-underline">Print QR</a>', url)
    print_qr.short_description = "Storefront QR"

@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ('user', 'tenant', 'branch', 'role', 'is_2fa_enabled')
    list_filter = ('role', 'tenant', 'branch', 'is_2fa_enabled')
    search_fields = ('user__username', 'user__email', 'tenant__name')
    fields = ('user', 'tenant', 'branch', 'role', 'is_2fa_enabled', 'pos_pin')

@admin.register(APIKey)
class APIKeyAdmin(ModelAdmin):
    list_display = ('name', 'tenant', 'branch', 'key_prefix', 'is_active', 'created_at', 'last_used_at')
    list_filter = ('is_active', 'tenant', 'branch', 'created_at')
    search_fields = ('name', 'key_prefix', 'tenant__name', 'branch__name')
    readonly_fields = ('key_prefix', 'key_hash', 'created_at', 'last_used_at')
    fields = ('name', 'tenant', 'branch', 'key_prefix', 'key_hash', 'is_active', 'created_at', 'last_used_at')
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        # Prevent manual creation - keys should be generated programmatically
        return False

@admin.register(Attendance)
class AttendanceAdmin(ModelAdmin):
    list_display = ('user', 'branch', 'clock_in', 'clock_out', 'duration')
    list_filter = ('branch', 'clock_in')
    search_fields = ('user__user__username',)
    date_hierarchy = 'clock_in'

@admin.register(ActivityLog)
class ActivityLogAdmin(ModelAdmin):
    list_display = ('actor', 'action_type', 'target_model', 'timestamp', 'ip_address')
    list_filter = ('action_type', 'tenant', 'timestamp')
    search_fields = ('actor__user__username', 'description', 'target_model')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)

@admin.register(SystemLog)
class SystemLogAdmin(ModelAdmin):
    list_display = ('created_at', 'level', 'module', 'short_message', 'path')
    list_filter = ('level', 'created_at', 'module')
    search_fields = ('message', 'traceback', 'module', 'path')
    readonly_fields = ('level', 'module', 'message', 'traceback', 'path', 'created_at')
    ordering = ('-created_at',)

    def short_message(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    short_message.short_description = 'Message'

    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(CrossTenantAuditLog)
class CrossTenantAuditLogAdmin(ModelAdmin):
    list_display = ('timestamp', 'user', 'action_type', 'accessed_tenant', 'user_home_tenant', 'target_model', 'ip_address')
    list_filter = ('action_type', 'accessed_tenant', 'user_home_tenant', 'timestamp')
    search_fields = ('user__username', 'description', 'target_model', 'target_object_repr')
    readonly_fields = ('user', 'accessed_tenant', 'user_home_tenant', 'action_type', 'target_model', 
                      'target_object_id', 'target_object_repr', 'description', 'ip_address', 
                      'user_agent', 'timestamp')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Only allow deletion of old logs
        return request.user.is_superuser
@admin.register(SEOSettings)
class SEOSettingsAdmin(ModelAdmin):
    list_display = ('tenant', 'meta_title', 'homepage_video_id', 'updated_at')
    search_fields = ('tenant__name', 'meta_title')
    readonly_fields = ('updated_at',)
    fieldsets = (
        (None, {
            "fields": ("tenant", "meta_title", "meta_description", "keywords"),
        }),
        ("Social & Open Graph", {
            "fields": ("og_title", "og_description", "og_image"),
        }),
        ("Tracking & Analytics", {
            "fields": ("google_analytics_id", "facebook_pixel_id"),
        }),
        ("Homepage Settings", {
            "fields": ("homepage_video_id",),
        }),
        ("Contact Information", {
            "fields": ("contact_email", "support_email", "contact_phone", "contact_address", "office_hours"),
        }),
        ("Metadata", {
            "fields": ("updated_at",),
        }),
    )
