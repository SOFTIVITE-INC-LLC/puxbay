from django.http import FileResponse, HttpResponseForbidden
from django.utils.html import format_html
from django.urls import path, reverse
from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import DatabaseBackup
import os

@admin.register(DatabaseBackup)
class DatabaseBackupAdmin(ModelAdmin):
    list_display = ('filename', 'size_mb', 'created_at', 'download_link')
    readonly_fields = ('filename', 'file_path', 'size_bytes', 'created_at')
    search_fields = ('filename',)
    
    def download_link(self, obj):
        return format_html(
            '<a class="bg-primary-600 text-white px-3 py-2 rounded hover:bg-primary-700 transition" href="{}">Download</a>',
            reverse('admin:download_backup', args=[obj.pk])
        )
    download_link.short_description = "Action"
    download_link.allow_tags = True
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'download/<int:pk>/',
                self.admin_site.admin_view(self.download_backup),
                name='download_backup',
            ),
        ]
        return custom_urls + urls

    def download_backup(self, request, pk):
        if not request.user.has_perm('main.can_download_backup') and not request.user.is_superuser:
            return HttpResponseForbidden("You do not have permission to download backups.")

        backup = self.get_object(request, pk)
        if not backup or not os.path.exists(backup.file_path):
            self.message_user(request, "Backup file not found.", level='ERROR')
            return HttpResponseRedirect("../")

        response = FileResponse(open(backup.file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{backup.filename}"'
        return response
from unfold.admin import ModelAdmin, TabularInline
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
from .models import (
    ContactMessage, Category, Product, ProductHistory, Customer, Order, OrderItem,
    ExpenseCategory, Expense, TaxConfiguration, PaymentMethod, Payment, Return, ReturnItem,
    GiftCard, LoyaltyTransaction, StoreCreditTransaction, CRMSettings, CustomerTier,
    MarketingCampaign, CustomerFeedback, ProductComponent, FeedbackReport
)

@admin.register(FeedbackReport)
class FeedbackReportAdmin(ModelAdmin):
    list_display = ('subject', 'report_type', 'priority', 'status', 'tenant', 'created_at')
    list_filter = ('report_type', 'priority', 'status', 'tenant', 'created_at')
    search_fields = ('subject', 'message', 'tenant__name', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'tenant', 'user')
    ordering = ('-created_at',)
    
    list_editable = ('status', 'priority')
    
    fieldsets = (
        ('Report Details', {
            'fields': ('tenant', 'user', 'report_type', 'priority', 'subject', 'message', 'created_at')
        }),
        ('Admin Management', {
            'fields': ('status', 'admin_notes', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        if change and obj.user and ( 'status' in form.changed_data or 'admin_notes' in form.changed_data ):
            # Notify the user about the response
            from django.core.mail import send_mail
            from django.template.loader import render_to_string
            from django.utils.html import strip_tags
            from django.conf import settings
            
            subject = f"Update on your Puxbay Report: {obj.subject}"
            
            context = {
                'feedback': obj,
            }
            
            html_message = render_to_string('emails/feedback_response.html', context)
            plain_message = strip_tags(html_message)
            
            try:
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [obj.user.email],
                    html_message=html_message,
                    fail_silently=True,
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Feedback response email failed: {str(e)}")
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages



class TenantAdmin(ModelAdmin):
    """
    Admin class that hides models from the public schema admin.
    These models are only accessible via tenant-specific admin URLs.
    """
    def has_module_permission(self, request):
        return request.tenant.schema_name != 'public'
    
    def has_view_permission(self, request, obj=None):
         return request.tenant.schema_name != 'public'
    
    def has_add_permission(self, request):
        return request.tenant.schema_name != 'public'
        
    def has_change_permission(self, request, obj=None):
        return request.tenant.schema_name != 'public'
        
    def has_delete_permission(self, request, obj=None):
        return request.tenant.schema_name != 'public'
        
    def get_queryset(self, request):
        if request.tenant.schema_name == 'public':
            return self.model.objects.none()
        return super().get_queryset(request)

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(TenantAdmin):
    list_display = ('name', 'type', 'tenant', 'created_at')
    list_filter = ('type', 'tenant')
    search_fields = ('name', 'description')

@admin.register(Expense)
class ExpenseAdmin(TenantAdmin):
    list_display = ('category', 'amount', 'date', 'branch', 'tenant', 'created_by')
    list_filter = ('category', 'branch', 'date')
    search_fields = ('description',)
    date_hierarchy = 'date'

@admin.register(TaxConfiguration)
class TaxConfigurationAdmin(TenantAdmin):
    list_display = ('tenant', 'tax_type', 'tax_rate', 'is_active')
    list_filter = ('tax_type', 'is_active')

@admin.register(PaymentMethod)
class PaymentMethodAdmin(TenantAdmin):
    list_display = ('name', 'provider', 'tenant', 'is_active')
    list_filter = ('provider', 'is_active')

@admin.register(Payment)
class PaymentAdmin(TenantAdmin):
    list_display = ('id', 'order', 'payment_method', 'amount', 'status', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('transaction_id',)
    date_hierarchy = 'created_at'

class ReturnItemInline(TabularInline):
    model = ReturnItem
    extra = 1

@admin.register(Return)
class ReturnAdmin(TenantAdmin):
    list_display = ('id', 'order', 'customer', 'status', 'refund_amount', 'created_at')
    list_filter = ('status', 'reason', 'refund_method')
    search_fields = ('order__id', 'customer__name')
    date_hierarchy = 'created_at'
    inlines = [ReturnItemInline]

# CRM Models
@admin.register(GiftCard)
class GiftCardAdmin(TenantAdmin):
    list_display = ('code', 'balance', 'status', 'customer', 'expiry_date', 'created_at')
    list_filter = ('status', 'tenant', 'expiry_date')
    search_fields = ('code', 'customer__name')

@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(TenantAdmin):
    list_display = ('customer', 'points', 'transaction_type', 'order', 'created_at')
    list_filter = ('transaction_type', 'tenant', 'created_at')
    search_fields = ('customer__name', 'description')
    date_hierarchy = 'created_at'

@admin.register(StoreCreditTransaction)
class StoreCreditTransactionAdmin(TenantAdmin):
    list_display = ('customer', 'amount', 'reference', 'created_at')
    list_filter = ('tenant', 'created_at')
    search_fields = ('customer__name', 'reference')
    date_hierarchy = 'created_at'

@admin.register(CRMSettings)
class CRMSettingsAdmin(TenantAdmin):
    list_display = ('tenant', 'points_per_currency', 'redemption_rate')
    list_filter = ('tenant',)

@admin.register(CustomerTier)
class CustomerTierAdmin(TenantAdmin):
    list_display = ('name', 'min_spend', 'discount_percentage', 'tenant', 'color', 'icon')
    list_filter = ('tenant',)
    search_fields = ('name',)

@admin.register(MarketingCampaign)
class MarketingCampaignAdmin(TenantAdmin):
    list_display = ('name', 'campaign_type', 'status', 'target_tier', 'scheduled_at', 'sent_at')
    list_filter = ('campaign_type', 'status', 'tenant', 'scheduled_at')
    search_fields = ('name', 'subject', 'message')
    date_hierarchy = 'created_at'

@admin.register(CustomerFeedback)
class CustomerFeedbackAdmin(TenantAdmin):
    list_display = ('customer', 'rating', 'is_public', 'transaction', 'created_at')
    list_filter = ('rating', 'is_public', 'tenant', 'created_at')
    search_fields = ('customer__name', 'comment')
    date_hierarchy = 'created_at'

# Basic Models
class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Category)
class CategoryAdmin(TenantAdmin):
    list_display = ('name', 'tenant', 'branch')
    list_filter = ('tenant', 'branch')
    search_fields = ('name', 'description')

class ProductHistoryInline(TabularInline):
    model = ProductHistory
    extra = 0
    can_delete = False
    fields = ('action', 'changed_by', 'changed_at', 'changes_summary', 'view_details')
    readonly_fields = ('action', 'changed_by', 'changed_at', 'changes_summary', 'view_details')
    ordering = ('-changed_at',)
    max_num = 10  # Show only last 10 changes inline
    
    def view_details(self, obj):
        if obj.id:
            url = reverse('admin:main_producthistory_change', args=[obj.id])
            return format_html('<a href="{}" target="_blank">View Details</a>', url)
        return "-"
    view_details.short_description = "Details"

class ProductComponentInline(TabularInline):
    model = ProductComponent
    fk_name = 'parent_product'
    extra = 1
    autocomplete_fields = ['component_product']

@admin.register(Product)
class ProductAdmin(TenantAdmin):
    list_display = ('name', 'sku', 'price', 'stock_quantity', 'category', 'branch', 'is_composite', 'is_active', 'history_count')
    list_filter = ('category', 'branch', 'tenant', 'is_active')
    search_fields = ('name', 'sku', 'barcode')
    readonly_fields = ('created_at', 'updated_at', 'history_count')
    inlines = [ProductComponentInline, ProductHistoryInline]
    
    def history_count(self, obj):
        if obj.id:
            count = obj.history.count()
            url = reverse('admin:main_producthistory_changelist') + f'?product_id_snapshot={obj.id}'
            return format_html('<a href="{}">{} changes</a>', url, count)
        return "0 changes"
    history_count.short_description = "History"

@admin.register(Customer)
class CustomerAdmin(TenantAdmin):
    list_display = ('name', 'email', 'phone', 'customer_type', 'tier', 'loyalty_points', 'total_spend')
    list_filter = ('customer_type', 'tier', 'tenant', 'marketing_opt_in')
    search_fields = ('name', 'email', 'phone')

@admin.register(Order)
class OrderAdmin(TenantAdmin):
    list_display = ('id', 'customer', 'branch', 'total_amount', 'payment_method', 'status', 'ordering_type', 'created_at')
    list_filter = ('status', 'payment_method', 'ordering_type', 'branch', 'tenant', 'created_at')
    search_fields = ('customer__name', 'offline_uuid')
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]



# Product History Admin
@admin.register(ProductHistory)
class ProductHistoryAdmin(TenantAdmin):
    list_display = ('product_name', 'action', 'changed_by_user', 'changed_at', 'changes_summary_short', 'revert_link')
    list_filter = ('action', 'changed_at', 'tenant')
    search_fields = ('snapshot_data__name', 'snapshot_data__sku', 'changes_summary')
    readonly_fields = ('product', 'product_id_snapshot', 'action', 'changed_by', 'changed_at', 'snapshot_data', 'changes_summary', 'tenant', 'formatted_snapshot')
    date_hierarchy = 'changed_at'
    ordering = ('-changed_at',)
    actions = ['revert_to_version']

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('revert/<uuid:history_id>/', self.admin_site.admin_view(self.revert_view), name='revert_product_history'),
        ]
        return custom_urls + urls

    def revert_view(self, request, history_id):
        from django.shortcuts import get_object_or_404, redirect
        from django.contrib import messages
        from decimal import Decimal
        from datetime import datetime

        history = get_object_or_404(ProductHistory, pk=history_id)
        
        if history.action == 'deleted':
            self.message_user(request, 'Cannot revert to a deleted product state. Please create a new product instead.', level=messages.ERROR)
            return redirect('admin:main_producthistory_changelist')
        
        if not history.product:
            self.message_user(request, 'Cannot revert: Product no longer exists.', level=messages.ERROR)
            return redirect('admin:main_producthistory_changelist')
            
        product = history.product
        snapshot = history.snapshot_data
        
        # Update product fields from snapshot
        product.name = snapshot.get('name', product.name)
        product.sku = snapshot.get('sku', product.sku)
        product.price = Decimal(snapshot.get('price', str(product.price)))
        product.stock_quantity = snapshot.get('stock_quantity', product.stock_quantity)
        product.description = snapshot.get('description', product.description)
        product.barcode = snapshot.get('barcode')
        product.batch_number = snapshot.get('batch_number')
        product.invoice_waybill_number = snapshot.get('invoice_waybill_number')
        product.cost_price = Decimal(snapshot.get('cost_price', str(product.cost_price)))
        product.low_stock_threshold = snapshot.get('low_stock_threshold', product.low_stock_threshold)
        product.country_of_origin = snapshot.get('country_of_origin')
        product.manufacturer_name = snapshot.get('manufacturer_name')
        product.manufacturer_address = snapshot.get('manufacturer_address')
        product.wholesale_price = Decimal(snapshot.get('wholesale_price', str(product.wholesale_price)))
        product.minimum_wholesale_quantity = snapshot.get('minimum_wholesale_quantity', product.minimum_wholesale_quantity)
        product.is_batch_tracked = snapshot.get('is_batch_tracked', product.is_batch_tracked)
        product.auto_reorder = snapshot.get('auto_reorder', product.auto_reorder)
        product.reorder_quantity = snapshot.get('reorder_quantity', product.reorder_quantity)
        product.is_active = snapshot.get('is_active', product.is_active)
        product.has_variants = snapshot.get('has_variants', product.has_variants)
        
        # Handle dates
        if snapshot.get('expiry_date'):
            product.expiry_date = datetime.fromisoformat(snapshot['expiry_date']).date()
        if snapshot.get('manufacturing_date'):
            product.manufacturing_date = datetime.fromisoformat(snapshot['manufacturing_date']).date()
        
        product.save()
        
        self.message_user(request, f'Successfully reverted "{product.name}" to version from {history.changed_at.strftime("%Y-%m-%d %H:%M")}', level=messages.SUCCESS)
        return redirect('admin:main_producthistory_changelist')

    
    def product_name(self, obj):
        return obj.snapshot_data.get('name', 'Unknown Product')
    product_name.short_description = 'Product'
    product_name.admin_order_field = 'snapshot_data__name'
    
    def changed_by_user(self, obj):
        if obj.changed_by:
            return obj.changed_by.user.username
        return 'System'
    changed_by_user.short_description = 'Changed By'
    
    def changes_summary_short(self, obj):
        summary = obj.changes_summary
        if len(summary) > 100:
            return summary[:100] + '...'
        return summary
    changes_summary_short.short_description = 'Changes'
    
    def formatted_snapshot(self, obj):
        """Display snapshot data in a readable format"""
        import json
        formatted = json.dumps(obj.snapshot_data, indent=2)
        return format_html('<pre>{}</pre>', formatted)
    formatted_snapshot.short_description = 'Snapshot Data'
    
    def revert_link(self, obj):
        if obj.action != 'deleted' and obj.product:
            url = reverse('admin:revert_product_history', args=[obj.id])
            return format_html('<a href="{}" class="button">Revert to this version</a>', url)
        return "-"
    revert_link.short_description = 'Actions'
    
    def revert_to_version(self, request, queryset):
        """Admin action to revert products to selected versions"""
        if queryset.count() != 1:
            self.message_user(request, 'Please select exactly one history entry to revert.', level=messages.WARNING)
            return
        
        history = queryset.first()
        if history.action == 'deleted':
            self.message_user(request, 'Cannot revert to a deleted product state. Please create a new product instead.', level=messages.ERROR)
            return
        
        if not history.product:
            self.message_user(request, 'Cannot revert: Product no longer exists.', level=messages.ERROR)
            return
        
        # Revert the product
        from decimal import Decimal
        from datetime import datetime
        
        product = history.product
        snapshot = history.snapshot_data
        
        # Update product fields from snapshot
        product.name = snapshot.get('name', product.name)
        product.sku = snapshot.get('sku', product.sku)
        product.price = Decimal(snapshot.get('price', str(product.price)))
        product.stock_quantity = snapshot.get('stock_quantity', product.stock_quantity)
        product.description = snapshot.get('description', product.description)
        product.barcode = snapshot.get('barcode')
        product.batch_number = snapshot.get('batch_number')
        product.invoice_waybill_number = snapshot.get('invoice_waybill_number')
        product.cost_price = Decimal(snapshot.get('cost_price', str(product.cost_price)))
        product.low_stock_threshold = snapshot.get('low_stock_threshold', product.low_stock_threshold)
        product.country_of_origin = snapshot.get('country_of_origin')
        product.manufacturer_name = snapshot.get('manufacturer_name')
        product.manufacturer_address = snapshot.get('manufacturer_address')
        product.wholesale_price = Decimal(snapshot.get('wholesale_price', str(product.wholesale_price)))
        product.minimum_wholesale_quantity = snapshot.get('minimum_wholesale_quantity', product.minimum_wholesale_quantity)
        product.is_batch_tracked = snapshot.get('is_batch_tracked', product.is_batch_tracked)
        product.auto_reorder = snapshot.get('auto_reorder', product.auto_reorder)
        product.reorder_quantity = snapshot.get('reorder_quantity', product.reorder_quantity)
        product.is_active = snapshot.get('is_active', product.is_active)
        product.has_variants = snapshot.get('has_variants', product.has_variants)
        
        # Handle dates
        if snapshot.get('expiry_date'):
            product.expiry_date = datetime.fromisoformat(snapshot['expiry_date']).date()
        if snapshot.get('manufacturing_date'):
            product.manufacturing_date = datetime.fromisoformat(snapshot['manufacturing_date']).date()
        
        product.save()
        
        self.message_user(request, f'Successfully reverted "{product.name}" to version from {history.changed_at.strftime("%Y-%m-%d %H:%M")}', level=messages.SUCCESS)
    
    revert_to_version.short_description = 'Revert to selected version'

