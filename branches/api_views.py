from rest_framework import viewsets, permissions, filters, parsers
from decimal import Decimal
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, F, Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta, datetime
from django_filters.rest_framework import DjangoFilterBackend
from main.models import (
    Category, Product, Customer, Order,
    CustomerFeedback, GiftCard, Return,
    Expense, ExpenseCategory, PaymentMethod,
    ProductComponent, ProductHistory,
    CustomerTier, LoyaltyTransaction, StoreCreditTransaction, 
    TaxConfiguration
)
from notifications.models import Notification
from accounts.models import Branch, UserProfile
from .models import (
    Supplier, PurchaseOrder, StockTransfer, 
    StocktakeSession, CashDrawerSession
)
from api.base_views import StandardizedViewSet, StandardizedReadOnlyViewSet
from .api_serializers import (
    CategorySerializer, ProductSerializer, 
    CustomerSerializer, OrderSerializer, OrderCreateSerializer,
    SupplierSerializer, PurchaseOrderSerializer, StockTransferSerializer,
    StocktakeSessionSerializer, CashDrawerSessionSerializer,
    NotificationSerializer, CustomerFeedbackSerializer, GiftCardSerializer,
    ReturnSerializer, ExpenseSerializer, ExpenseCategorySerializer, PaymentMethodSerializer,
    BranchSerializer, ProductHistorySerializer, ProductComponentSerializer,
    CustomerTierSerializer, LoyaltyTransactionSerializer, StoreCreditTransactionSerializer,
    TaxConfigurationSerializer, StaffSerializer
)

class CategoryViewSet(StandardizedViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Category.objects.none()
        # Filter by tenant
        return Category.objects.filter(tenant=self.request.user.profile.tenant).select_related('branch')

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.profile.tenant)

class ProductViewSet(StandardizedViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'low_stock_threshold']
    search_fields = ['name', 'sku', 'barcode']
    ordering_fields = ['name', 'price', 'stock_quantity']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Product.objects.none()
        return Product.objects.filter(tenant=self.request.user.profile.tenant).select_related('category', 'branch')

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.profile.tenant)

    @action(detail=True, methods=['post'])
    def stock_adjustment(self, request, pk=None):
        """Manually adjust stock with audit logging"""
        product = self.get_object()
        adjustment = request.data.get('adjustment', 0)
        reason = request.data.get('reason', 'Manual Adjustment')
        
        try:
            adjustment = int(adjustment)
        except ValueError:
            return Response({'error': 'Adjustment must be an integer'}, status=400)
            
        old_quantity = product.stock_quantity
        product.stock_quantity += adjustment
        product.save()
        
        # Create audit entry
        ProductHistory.objects.create(
            product=product,
            product_id_snapshot=product.id,
            action='updated',
            changed_by=request.user.profile,
            tenant=request.user.profile.tenant,
            snapshot_data={'stock_quantity': product.stock_quantity},
            changes_summary=f"Stock adjusted by {adjustment} ({old_quantity} -> {product.stock_quantity}). Reason: {reason}"
        )
        
        return Response({
            'status': 'Stock adjusted',
            'new_quantity': product.stock_quantity
        })

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get audit history for this product"""
        product = self.get_object()
        history = ProductHistory.objects.filter(product=product).order_by('-changed_at')
        serializer = ProductHistorySerializer(history, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create products (max 50)"""
        if not isinstance(request.data, list):
            return Response({'error': 'Expected a list of products'}, status=400)
        
        if len(request.data) > 50:
            return Response({'error': 'Maximum 50 products per bulk request'}, status=400)
            
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        # Manually set tenant for all
        self.perform_bulk_create(serializer)
        return Response(serializer.data, status=201)

    def perform_bulk_create(self, serializer):
        serializer.save(tenant=self.request.user.profile.tenant)

class CustomerViewSet(StandardizedViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['name', 'created_at', 'total_spend']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Customer.objects.none()
        return Customer.objects.filter(tenant=self.request.user.profile.tenant).select_related('branch', 'tier')

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.profile.tenant)

    @action(detail=True, methods=['post'])
    def adjust_loyalty_points(self, request, pk=None):
        """Manually add or subtract loyalty points"""
        customer = self.get_object()
        points = request.data.get('points', 0)
        description = request.data.get('description', 'Manual Adjustment')
        
        try:
            points = float(points)
        except ValueError:
            return Response({'error': 'Points must be a number'}, status=400)
            
        customer.loyalty_points += Decimal(str(points))
        customer.save()
        
        # Create transaction record
        LoyaltyTransaction.objects.create(
            tenant=request.user.profile.tenant,
            customer=customer,
            points=points,
            transaction_type='adjustment',
            description=description
        )
        
        return Response({
            'status': 'Loyalty points adjusted',
            'new_balance': customer.loyalty_points
        })

    @action(detail=True, methods=['post'])
    def adjust_store_credit(self, request, pk=None):
        """Manually add or subtract store credit"""
        customer = self.get_object()
        amount = request.data.get('amount', 0)
        reference = request.data.get('reference', 'Manual Adjustment')
        
        try:
            amount = float(amount)
        except ValueError:
            return Response({'error': 'Amount must be a number'}, status=400)
            
        customer.store_credit_balance += Decimal(str(amount))
        customer.save()
        
        # Create transaction record
        StoreCreditTransaction.objects.create(
            tenant=request.user.profile.tenant,
            customer=customer,
            amount=amount,
            reference=reference
        )
        
        return Response({
            'status': 'Store credit adjusted',
            'new_balance': customer.store_credit_balance
        })

    @action(detail=True, methods=['post'])
    def refresh_tier(self, request, pk=None):
        """Recalculate customer tier based on spend"""
        customer = self.get_object()
        updated = customer.calculate_tier()
        return Response({
            'status': 'Tier check completed',
            'tier_updated': updated,
            'current_tier': customer.tier.name if customer.tier else None
        })

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create customers (max 50)"""
        if not isinstance(request.data, list):
            return Response({'error': 'Expected a list of customers'}, status=400)
        
        if len(request.data) > 50:
            return Response({'error': 'Maximum 50 customers per bulk request'}, status=400)
            
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(tenant=self.request.user.profile.tenant)
        return Response(serializer.data, status=201)

class OrderViewSet(StandardizedViewSet):
    queryset = Order.objects.all()
    # Use different serializer for list vs create
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'ordering_type']
    ordering_fields = ['created_at', 'total_amount']

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Order.objects.none()
        return Order.objects.filter(tenant=self.request.user.profile.tenant).select_related(
            'customer', 'branch', 'cashier__user'
        ).prefetch_related('items__product')

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.user.profile.tenant,
            cashier=self.request.user.profile,
            branch=self.request.user.profile.branch
        )

class ReportViewSet(viewsets.ViewSet):
    """
    ViewSet for Reports & Analytics
    Not bound to a specific model, but aggregates data.
    """

    def _get_date_range(self, request):
        range_type = request.query_params.get('range', 'month')
        start_str = request.query_params.get('start_date')
        end_str = request.query_params.get('end_date')
        
        now = timezone.now()
        start_date = None
        end_date = now.date()
        
        if range_type == 'today':
            start_date = now.date()
        elif range_type == 'week':
            start_date = (now - timedelta(days=7)).date()
        elif range_type == 'month':
            start_date = (now - timedelta(days=30)).date()
        elif range_type == 'year':
            start_date = (now - timedelta(days=365)).date()
        elif range_type == 'custom' and start_str and end_str:
            try:
                start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        return start_date, end_date

    @action(detail=False, methods=['get'])
    def financial_summary(self, request):
        tenant = request.user.profile.tenant
        start_date, end_date = self._get_date_range(request)
        
        orders = Order.objects.filter(tenant=tenant, status='completed')
        if start_date:
            orders = orders.filter(created_at__date__gte=start_date)
        if end_date:
            orders = orders.filter(created_at__date__lte=end_date)
            
        total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_orders = orders.count()
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        return Response({
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'avg_order_value': avg_order_value,
            'period': {
                'start': start_date,
                'end': end_date
            }
        })

    @action(detail=False, methods=['get'])
    def daily_sales(self, request):
        tenant = request.user.profile.tenant
        start_date, end_date = self._get_date_range(request)
        
        if not start_date: # Default to 30 days if not specified for chart
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)

        orders = Order.objects.filter(
            tenant=tenant, 
            status='completed',
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        daily_data = orders.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            revenue=Sum('total_amount'),
            orders=Count('id')
        ).order_by('date')
        
        return Response(list(daily_data))

    @action(detail=False, methods=['get'])
    def top_products(self, request):
        tenant = request.user.profile.tenant
        # We need OrderItems for this, but currently imported models are limited
        # Let's import locally or add to top
        from main.models import OrderItem
        
        start_date, end_date = self._get_date_range(request)
        
        items = OrderItem.objects.filter(order__tenant=tenant, order__status='completed')
        if start_date:
            items = items.filter(order__created_at__date__gte=start_date)
        if end_date:
            items = items.filter(order__created_at__date__lte=end_date)
            
        top_items = items.values(
            'product__id', 'product__name', 'product__sku'
        ).annotate(
            quantity_sold=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity'))
        ).order_by('-quantity_sold')[:10]
        
        return Response(list(top_items))

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """List products below their threshold"""
        products = Product.objects.filter(
            tenant=request.user.profile.tenant,
            stock_quantity__lte=F('low_stock_threshold'),
            is_active=True
        ).values('id', 'name', 'sku', 'stock_quantity', 'low_stock_threshold')[:20]
        return Response(list(products))

    @action(detail=False, methods=['get'])
    def restock_recommendations(self, request):
        """AI-lite: Simple sales-trend based restock suggestions"""
        from django.utils import timezone
        from datetime import timedelta
        from main.models import OrderItem # Import locally if not already at top
        
        tenant = request.user.profile.tenant
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Calculate avg daily sales per product over last 30 days
        sales_summary = OrderItem.objects.filter(
            order__tenant=tenant,
            order__status='completed',
            order__created_at__gte=thirty_days_ago
        ).values('product', 'product__name', 'product__sku', 'product__stock_quantity').annotate(
            total_sold=Sum('quantity'),
            avg_daily_sales=Sum('quantity') / 30.0
        )
        
        recommendations = []
        for item in sales_summary:
            stock = item['product__stock_quantity']
            avg = float(item['avg_daily_sales'])
            # Safety stock = 1 week of sales
            safety_stock = avg * 7
            
            if stock < safety_stock:
                recommendations.append({
                    'product_id': item['product'],
                    'name': item['product__name'],
                    'sku': item['product__sku'],
                    'current_stock': stock,
                    'avg_daily_sales': round(avg, 2),
                    'recommended_restock': int(round((avg * 14) - stock)) # Restock to 2 weeks levels
                })
                
        return Response(recommendations)

# -----------------------------------------------------------------------------
# Supply Chain ViewSets
# -----------------------------------------------------------------------------

class SupplierViewSet(StandardizedViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'email', 'contact_person']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Supplier.objects.none()
        return Supplier.objects.filter(tenant=self.request.user.profile.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.profile.tenant)

class PurchaseOrderViewSet(StandardizedViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'supplier']
    ordering_fields = ['created_at', 'expected_date']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return PurchaseOrder.objects.none()
        return PurchaseOrder.objects.filter(tenant=self.request.user.profile.tenant).select_related(
            'supplier', 'branch', 'created_by__user'
        ).prefetch_related('items__product')

    def perform_create(self, serializer):
        # Ensure branch is set to user's branch if not provided (though serializer might require it)
        branch = serializer.validated_data.get('branch', self.request.user.profile.branch)
        serializer.save(
            tenant=self.request.user.profile.tenant,
            created_by=self.request.user.profile
        )

class StockTransferViewSet(StandardizedViewSet):
    queryset = StockTransfer.objects.all()
    serializer_class = StockTransferSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'source_branch', 'destination_branch']
    ordering_fields = ['created_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return StockTransfer.objects.none()
        tenant = self.request.user.profile.tenant
        return StockTransfer.objects.filter(tenant=tenant).select_related(
            'source_branch', 'destination_branch', 'created_by__user'
        ).prefetch_related('items__product')

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.user.profile.tenant,
            created_by=self.request.user.profile
        )

# -----------------------------------------------------------------------------
# Store Operations ViewSets
# -----------------------------------------------------------------------------

class StocktakeViewSet(StandardizedViewSet):
    queryset = StocktakeSession.objects.all()
    serializer_class = StocktakeSessionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'branch']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return StocktakeSession.objects.none()
        # Filter by user's branch usually, but let's allow tenant scope for now
        return StocktakeSession.objects.filter(
            branch__tenant=self.request.user.profile.tenant
        ).select_related('branch', 'created_by__user').prefetch_related('entries__product')

    def perform_create(self, serializer):
        # Auto-assign branch if missing? Or require it.
        # Assuming branch is passed in payload
        serializer.save(created_by=self.request.user.profile)

class CashDrawerViewSet(StandardizedViewSet):
    queryset = CashDrawerSession.objects.all()
    serializer_class = CashDrawerSessionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'branch', 'employee']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return CashDrawerSession.objects.none()
        return CashDrawerSession.objects.filter(
            tenant=self.request.user.profile.tenant
        ).select_related('branch', 'employee__user')

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.user.profile.tenant,
            employee=self.request.user.profile # Auto assign current user as employee
        )

# -----------------------------------------------------------------------------
# Notifications & CRM ViewSets
# -----------------------------------------------------------------------------

class NotificationViewSet(StandardizedViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    http_method_names = ['get', 'put', 'patch', 'head'] # No delete/create for now

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Notification.objects.none()
        # Notifications are per-user
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'marked all as read'})

class FeedbackViewSet(StandardizedViewSet):
    queryset = CustomerFeedback.objects.all()
    serializer_class = CustomerFeedbackSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return CustomerFeedback.objects.none()
        return CustomerFeedback.objects.filter(tenant=self.request.user.profile.tenant).select_related('customer', 'transaction')

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.profile.tenant)

class GiftCardViewSet(StandardizedViewSet):
    queryset = GiftCard.objects.all()
    serializer_class = GiftCardSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['code']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return GiftCard.objects.none()
        return GiftCard.objects.filter(tenant=self.request.user.profile.tenant).select_related('customer')

# -----------------------------------------------------------------------------
# Returns & Financial ViewSets
# -----------------------------------------------------------------------------

class ReturnViewSet(StandardizedViewSet):
    queryset = Return.objects.all()
    serializer_class = ReturnSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['status']
    search_fields = ['order__order_number', 'customer__name']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Return.objects.none()
        return Return.objects.filter(tenant=self.request.user.profile.tenant).select_related(
            'order', 'customer', 'created_by__user'
        ).prefetch_related('items__product')

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.user.profile.tenant,
            created_by=self.request.user.profile
        )

class ExpenseViewSet(StandardizedViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'date']
    parser_classes = (parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Expense.objects.none()
        return Expense.objects.filter(tenant=self.request.user.profile.tenant).select_related(
            'category', 'branch', 'created_by__user'
        )

    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.user.profile.tenant,
            created_by=self.request.user.profile
        )

class ExpenseCategoryViewSet(StandardizedViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return ExpenseCategory.objects.none()
        return ExpenseCategory.objects.filter(tenant=self.request.user.profile.tenant)

class PaymentMethodViewSet(StandardizedReadOnlyViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return PaymentMethod.objects.none()
        return PaymentMethod.objects.filter(tenant=self.request.user.profile.tenant, is_active=True)

class BranchViewSet(StandardizedViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'unique_id']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Branch.objects.none()
        return Branch.objects.filter(tenant=self.request.user.profile.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.profile.tenant)

class ProductHistoryViewSet(StandardizedReadOnlyViewSet):
    queryset = ProductHistory.objects.all()
    serializer_class = ProductHistorySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action', 'product']
    ordering_fields = ['changed_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return ProductHistory.objects.none()
        return ProductHistory.objects.filter(tenant=self.request.user.profile.tenant)

class ProductComponentViewSet(StandardizedViewSet):
    queryset = ProductComponent.objects.all()
    serializer_class = ProductComponentSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return ProductComponent.objects.none()
        return ProductComponent.objects.filter(parent_product__tenant=self.request.user.profile.tenant)

    def perform_create(self, serializer):
        # Validation is handled by serializer/model (unique_together)
        serializer.save()

class CustomerTierViewSet(StandardizedViewSet):
    queryset = CustomerTier.objects.all()
    serializer_class = CustomerTierSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return CustomerTier.objects.none()
        return CustomerTier.objects.filter(tenant=self.request.user.profile.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.profile.tenant)

class LoyaltyTransactionViewSet(StandardizedReadOnlyViewSet):
    queryset = LoyaltyTransaction.objects.all()
    serializer_class = LoyaltyTransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['customer', 'transaction_type']
    ordering_fields = ['created_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return LoyaltyTransaction.objects.none()
        return LoyaltyTransaction.objects.filter(tenant=self.request.user.profile.tenant)

class StoreCreditTransactionViewSet(StandardizedReadOnlyViewSet):
    queryset = StoreCreditTransaction.objects.all()
    serializer_class = StoreCreditTransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['customer']
    ordering_fields = ['created_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return StoreCreditTransaction.objects.none()
        return StoreCreditTransaction.objects.filter(tenant=self.request.user.profile.tenant)

class TaxConfigurationViewSet(StandardizedViewSet):
    queryset = TaxConfiguration.objects.all()
    serializer_class = TaxConfigurationSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return TaxConfiguration.objects.none()
        return TaxConfiguration.objects.filter(tenant=self.request.user.profile.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.profile.tenant)

class StaffViewSet(StandardizedReadOnlyViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = StaffSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'role']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return UserProfile.objects.none()
        return UserProfile.objects.filter(tenant=self.request.user.profile.tenant).select_related('user', 'branch')
