from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from main.admin import TenantAdmin  # Import the TenantAdmin we created
from .models import (
    StockTransfer, StockTransferItem, StockBatch, StockMovement,
    Supplier, PurchaseOrder, PurchaseOrderItem, CashDrawerSession,
    StocktakeSession, StocktakeEntry
)

class StockTransferItemInline(TabularInline):
    model = StockTransferItem
    extra = 1

@admin.register(StockTransfer)
class StockTransferAdmin(TenantAdmin):
    list_display = ('reference_id', 'source_branch', 'destination_branch', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'tenant', 'created_at')
    search_fields = ('reference_id', 'notes')
    date_hierarchy = 'created_at'
    inlines = [StockTransferItemInline]

@admin.register(StockBatch)
class StockBatchAdmin(TenantAdmin):
    list_display = ('product', 'batch_number', 'quantity', 'expiry_date', 'branch', 'is_expired')
    list_filter = ('branch', 'tenant', 'expiry_date', 'received_date')
    search_fields = ('batch_number', 'product__name')
    date_hierarchy = 'received_date'

@admin.register(StockMovement)
class StockMovementAdmin(TenantAdmin):
    list_display = ('product', 'movement_type', 'quantity_change', 'balance_after', 'branch', 'created_at')
    list_filter = ('movement_type', 'branch', 'tenant', 'created_at')
    search_fields = ('product__name', 'reference', 'notes')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

@admin.register(Supplier)
class SupplierAdmin(TenantAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone', 'tenant', 'created_at')
    list_filter = ('tenant', 'created_at')
    search_fields = ('name', 'contact_person', 'email', 'phone')

class PurchaseOrderItemInline(TabularInline):
    model = PurchaseOrderItem
    extra = 1

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(TenantAdmin):
    list_display = ('reference_id', 'supplier', 'branch', 'status', 'total_cost', 'created_at', 'expected_date')
    list_filter = ('status', 'branch', 'tenant', 'created_at')
    search_fields = ('reference_id', 'supplier__name', 'notes')
    date_hierarchy = 'created_at'
    inlines = [PurchaseOrderItemInline]

@admin.register(CashDrawerSession)
class CashDrawerSessionAdmin(TenantAdmin):
    list_display = ('id', 'branch', 'employee', 'status', 'start_time', 'end_time', 'difference')
    list_filter = ('status', 'branch', 'tenant', 'start_time')
    search_fields = ('employee__user__username', 'notes')
    date_hierarchy = 'start_time'
    readonly_fields = ('start_time',)

class StocktakeEntryInline(TabularInline):
    model = StocktakeEntry
    extra = 1
    readonly_fields = ('updated_at',)

@admin.register(StocktakeSession)
class StocktakeSessionAdmin(TenantAdmin):
    list_display = ('id', 'branch', 'created_by', 'status', 'started_at', 'completed_at')
    list_filter = ('status', 'branch', 'started_at')
    search_fields = ('created_by__user__username', 'notes')
    date_hierarchy = 'started_at'
    inlines = [StocktakeEntryInline]

