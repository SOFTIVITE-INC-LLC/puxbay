from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import LogoutAPIView, CurrentUserAPIView, WebhookViewSet, WebhookEventViewSet, OfflineSyncViewSet, KioskViewSet
from .health_views import SyncHealthViewSet
from branches.api_views import (
    ProductViewSet, CategoryViewSet, CustomerViewSet, 
    OrderViewSet, ReportViewSet, SupplierViewSet, 
    PurchaseOrderViewSet, StockTransferViewSet,
    StocktakeViewSet, CashDrawerViewSet,
    NotificationViewSet, FeedbackViewSet, GiftCardViewSet,
    ReturnViewSet, ExpenseViewSet, ExpenseCategoryViewSet, PaymentMethodViewSet,
    BranchViewSet, ProductHistoryViewSet, ProductComponentViewSet,
    CustomerTierViewSet, LoyaltyTransactionViewSet, StoreCreditTransactionViewSet,
    TaxConfigurationViewSet, StaffViewSet
)

schema_view = get_schema_view(
   openapi.Info(
      title="Puxbay API",
      default_version='v1',
      description="Modern API for SaaS Point of Sale Management",
      terms_of_service="https://puxbay.com/terms/",
      contact=openapi.Contact(email="api@puxbay.com"),
      license=openapi.License(name="Proprietary"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
# ... (rest of router registrations)
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'reports', ReportViewSet, basename='reports')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchase-order')
router.register(r'stock-transfers', StockTransferViewSet, basename='stock-transfer')
router.register(r'stocktakes', StocktakeViewSet, basename='stocktake')
router.register(r'cash-drawers', CashDrawerViewSet, basename='cash-drawer')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'gift-cards', GiftCardViewSet, basename='gift-card')
router.register(r'returns', ReturnViewSet, basename='return')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'expense-categories', ExpenseCategoryViewSet, basename='expense-category')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'product-history', ProductHistoryViewSet, basename='product-history')
router.register(r'product-components', ProductComponentViewSet, basename='product-component')
router.register(r'customer-tiers', CustomerTierViewSet, basename='customer-tier')
router.register(r'loyalty-transactions', LoyaltyTransactionViewSet, basename='loyalty-transaction')
router.register(r'store-credit-transactions', StoreCreditTransactionViewSet, basename='store-credit-transaction')
router.register(r'tax-configuration', TaxConfigurationViewSet, basename='tax-configuration')
router.register(r'staff', StaffViewSet, basename='staff')
router.register(r'webhooks', WebhookViewSet, basename='webhook')
router.register(r'webhook-logs', WebhookEventViewSet, basename='webhook-log')
router.register(r'offline', OfflineSyncViewSet, basename='offline-sync')
router.register(r'health', SyncHealthViewSet, basename='sync-health')
router.register(r'kiosk', KioskViewSet, basename='kiosk')

auth_urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutAPIView.as_view(), name='auth_logout'),
    path('user/', CurrentUserAPIView.as_view(), name='auth_user_details'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include(auth_urlpatterns)),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
