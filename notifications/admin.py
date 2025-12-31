from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Notification, NotificationSetting

@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ('recipient', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)

@admin.register(NotificationSetting)
class NotificationSettingAdmin(ModelAdmin):
    list_display = ('user', 'email_notifications', 'low_stock_alerts', 'sales_reports', 'security_alerts', 'system_alerts')
    list_filter = ('email_notifications', 'low_stock_alerts', 'sales_reports')
    search_fields = ('user__username', 'user__email')
    list_editable = ('email_notifications', 'low_stock_alerts', 'sales_reports', 'security_alerts', 'system_alerts')
