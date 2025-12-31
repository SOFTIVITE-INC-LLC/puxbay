from rest_framework import status, views, permissions, viewsets, filters, authentication
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from accounts.models import WebhookEndpoint, WebhookEvent
from .serializers import UserProfileSerializer, WebhookEndpointSerializer, WebhookEventSerializer
from .base_views import StandardizedAPIView, StandardizedViewSet, StandardizedReadOnlyViewSet

class LogoutAPIView(StandardizedAPIView):

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class CurrentUserAPIView(StandardizedAPIView):

    def get(self, request):
        try:
            profile = getattr(request.user, 'profile', None)
            if profile:
                serializer = UserProfileSerializer(profile)
                return Response(serializer.data)
            raise Exception("Profile not found")
        except Exception:
             # Fallback for users without profile (e.g. pure superuser)
             return Response({
                'id': request.user.id, 
                'username': request.user.username,
                'email': request.user.email
             })

class WebhookViewSet(StandardizedViewSet):
    serializer_class = WebhookEndpointSerializer
    
    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        if not profile:
             return WebhookEndpoint.objects.none()
        return WebhookEndpoint.objects.filter(tenant=profile.tenant)

    def perform_create(self, serializer):
        profile = getattr(self.request.user, 'profile', None)
        if profile:
            serializer.save(tenant=profile.tenant)

    @action(detail=True, methods=['post'])
    def ping(self, request, pk=None):
        """Send a test payload to the webhook endpoint"""
        endpoint = self.get_object()
        from utils.webhooks import WebhookService
        payload = {
            'message': 'This is a test webhook from Puxbay POS',
            'test': True
        }
        WebhookService.trigger(endpoint.tenant, 'test.ping', payload)
        return Response({'status': 'Ping triggered'})

class WebhookEventViewSet(StandardizedReadOnlyViewSet):
    serializer_class = WebhookEventSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        if not profile:
             return WebhookEvent.objects.none()
        return WebhookEvent.objects.filter(endpoint__tenant=profile.tenant)

class OfflineSyncViewSet(StandardizedViewSet, viewsets.ViewSet):
    """
    Unified Endpoint for Offline Synchronization.
    """
    from .auth import APIKeyAuthentication, RequireAPIKey
    authentication_classes = [APIKeyAuthentication, authentication.SessionAuthentication]
    permission_classes = [RequireAPIKey | permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='transaction', permission_classes=[permissions.AllowAny])
    def sync_transaction(self, request):
        """
        Receive and process queued offline transactions.
        """
        from django.http import JsonResponse
        from django.shortcuts import get_object_or_404
        from accounts.models import Branch, UserProfile
        from main.models import Product, Order, OrderItem, Customer
        from branches.models import StockMovement, CashDrawerSession
        import json
        import datetime
        from django.utils import timezone
        
        try:
            # Data is already parsed by DRF, but if it's raw JSON body:
            data = request.data
            uuid = data.get('uuid')
            transaction_type = data.get('type')
            transaction_data = data.get('data')
            
            if not all([uuid, transaction_type, transaction_data]):
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Ensure tenant is set (Session Auth Fallback)
            if not hasattr(request, 'tenant'):
                if hasattr(request.user, 'profile'):
                    request.tenant = request.user.profile.tenant
                else:
                    return Response({'error': 'Tenant context missing'}, status=status.HTTP_400_BAD_REQUEST)

            # Idempotency Check
            if transaction_type == 'order':
                from branches.services.pos import POSService
                
                cashier_id = transaction_data.get('cashier_id')
                cashier = None
                if cashier_id:
                    cashier = UserProfile.objects.filter(user__id=cashier_id).first()
                if not cashier and hasattr(request.user, 'profile'):
                     cashier = request.user.profile
                
                pos_service = POSService(tenant=request.tenant, user_profile=cashier)
                result = pos_service.sync_order(uuid, transaction_data)
                
                if result['status'] == 'already_synced':
                    return Response({'status': 'exists', 'message': result['message']}, status=status.HTTP_200_OK)
                elif result['status'] == 'success':
                    return Response({
                        'status': 'success', 
                        'id': str(result['order_id']),
                        'order_number': result.get('order_number')
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': result['message']}, status=status.HTTP_400_BAD_REQUEST)

            elif transaction_type == 'complete_order':
                from branches.services.pos import POSService
                order_id = transaction_data.get('order_id')
                cashier_id = transaction_data.get('cashier_id')
                
                if not order_id:
                    return Response({'error': 'order_id required'}, status=status.HTTP_400_BAD_REQUEST)
                
                cashier = None
                if cashier_id:
                    cashier = UserProfile.objects.filter(user__id=cashier_id).first()
                
                pos_service = POSService(tenant=request.tenant, user_profile=cashier)
                result = pos_service.complete_pending_order(order_id)
                
                if result['status'] == 'success':
                    return Response({'status': 'success', 'message': result['message']})
                else:
                    return Response({'error': result['message']}, status=status.HTTP_400_BAD_REQUEST)

            elif transaction_type == 'shift_close':
                 # Logic for shift close
                 pass

            elif transaction_type == 'create_po':
                from branches.services.purchase_orders import PurchaseOrderService
                from accounts.models import Branch
                
                branch_id = transaction_data.get('branch_id')
                supplier_id = transaction_data.get('supplier')
                expected_date = transaction_data.get('expected_date')
                items = transaction_data.get('items')
                
                if not all([branch_id, supplier_id, items]):
                    return Response({'error': 'branch_id, supplier, and items are required'}, status=status.HTTP_400_BAD_REQUEST)
                
                branch = get_object_or_404(Branch, pk=branch_id, tenant=request.tenant)
                
                user_profile = getattr(request.user, 'profile', None) if request.user.is_authenticated else None
                po_service = PurchaseOrderService(tenant=request.tenant, user_profile=user_profile)
                result = po_service.create_po(
                    branch=branch,
                    supplier_id=supplier_id,
                    expected_date=expected_date,
                    items_data=items,
                    notes=transaction_data.get('notes'),
                    uuid=uuid
                )
                
                if result['status'] == 'already_synced':
                    return Response({'status': 'exists', 'message': result['message']}, status=status.HTTP_200_OK)
                elif result['status'] == 'success':
                    return Response({'status': 'success', 'id': result['po_id'], 'reference': result['reference_id']}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': result['message']}, status=status.HTTP_400_BAD_REQUEST)

            elif transaction_type == 'create_transfer':
                from branches.services.transfers import TransferService
                from accounts.models import Branch
                
                source_branch_id = transaction_data.get('source_branch_id')
                dest_branch_id = transaction_data.get('destination_branch')
                items = transaction_data.get('items')
                reference_id = transaction_data.get('reference_id')
                
                if not all([source_branch_id, dest_branch_id, items]):
                    return Response({'error': 'source_branch_id, destination_branch, and items are required'}, status=status.HTTP_400_BAD_REQUEST)
                
                source_branch = get_object_or_404(Branch, pk=source_branch_id, tenant=request.tenant)
                dest_branch = get_object_or_404(Branch, pk=dest_branch_id, tenant=request.tenant)
                
                user_profile = getattr(request.user, 'profile', None) if request.user.is_authenticated else None
                transfer_service = TransferService(tenant=request.tenant, user_profile=user_profile)
                
                # Enhanced idempotency check - check both UUID and reference_id
                from branches.models import StockTransfer
                existing = StockTransfer.objects.filter(
                    tenant=request.tenant
                ).filter(
                    Q(id=uuid) | Q(reference_id=reference_id)
                ).first()
                
                if existing:
                    return Response({
                        'status': 'exists', 
                        'message': 'Transfer already exists',
                        'id': str(existing.id),
                        'reference': existing.reference_id
                    }, status=status.HTTP_200_OK)
                
                try:
                    from django.db import transaction
                    with transaction.atomic():
                        transfer = transfer_service.request_transfer(
                            source_branch=source_branch,
                            destination_branch=dest_branch,
                            items_data=items,
                            notes=transaction_data.get('notes')
                        )
                        # Override ID to match offline UUID
                        transfer.id = uuid
                        transfer.save()
                    
                    return Response({'status': 'success', 'id': str(transfer.id), 'reference': transfer.reference_id}, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'status': 'ignored'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='pin-login')
    def pin_login(self, request):
        """
        Authenticate a staff member via PIN for the current branch.
        """
        from accounts.models import UserProfile
        from rest_framework_simplejwt.tokens import RefreshToken
        
        pin = request.data.get('pin')
        
        if not pin:
            return Response({'error': 'PIN is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get all profiles for the current tenant and branch
        # request.tenant and request.branch are set by APIKeyAuthentication
        if not hasattr(request, 'tenant') or not hasattr(request, 'branch'):
            return Response({'error': 'X-API-Key required for PIN login'}, status=status.HTTP_403_FORBIDDEN)
            
        profiles = UserProfile.objects.filter(
            tenant=request.tenant,
            branch=request.branch
        ).select_related('user')
        
        authenticated_profile = None
        for profile in profiles:
            # EncryptedTextField decrypts on access
            if profile.pos_pin == pin:
                authenticated_profile = profile
                break
                
        if not authenticated_profile:
            return Response({'error': 'Invalid PIN'}, status=status.HTTP_401_UNAUTHORIZED)
            
        # Generate JWT tokens for the user
        refresh = RefreshToken.for_user(authenticated_profile.user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': authenticated_profile.user.id,
                'username': authenticated_profile.user.username,
                'role': authenticated_profile.role,
                'name': f"{authenticated_profile.user.first_name} {authenticated_profile.user.last_name}".strip() or authenticated_profile.user.username
            }
        })

    @action(detail=False, methods=['get'], url_path='data/(?P<branch_id>[^/.]+)', permission_classes=[permissions.AllowAny])
    def sync_data(self, request, branch_id=None):
        """
        Fetch data for offline caching.
        """
        from django.shortcuts import get_object_or_404
        from accounts.models import Branch, UserProfile
        from main.models import Product, Customer, Category, CRMSettings
        from django.utils import timezone
        import datetime
        from branches.api_serializers import ProductSerializer, CategorySerializer, CustomerSerializer
        
        branch = get_object_or_404(Branch, pk=branch_id)
        
        from django_tenants.utils import schema_context
        from django.db import connection
        
        with schema_context(branch.tenant.schema_name):
            # Products
            products = Product.objects.filter(branch=branch, is_active=True)
            products_data = ProductSerializer(products, many=True).data
            
            # Categories
            categories = Category.objects.filter(branch=branch)
            categories_data = CategorySerializer(categories, many=True).data
            
            # Customers
            customers = Customer.objects.filter(tenant=branch.tenant)
            customers_data = CustomerSerializer(customers, many=True).data
            
            return Response({
                'products': products_data,
                'categories': categories_data,
                'customers': customers_data,
                'timestamp': timezone.now(),
                'server_schema': connection.get_schema(),
                'products_count': len(products_data),
                'debug_meta': {
                    'schema': connection.get_schema(),
                    'branch_id': str(branch.id),
                    'tenant_schema': branch.tenant.schema_name,
                    'product_count_filtered': products.count(),
                    'product_count_total': Product.objects.count(),
                }
            })

    @action(detail=False, methods=['get'], url_path='inventory/(?P<branch_id>[^/.]+)', permission_classes=[permissions.AllowAny])
    def inventory(self, request, branch_id=None):
        """
        Get current inventory levels.
        """
        from main.models import Product
        from django.shortcuts import get_object_or_404
        from accounts.models import Branch
        
        branch = get_object_or_404(Branch, pk=branch_id)
        
        from django.db import connection
        connection.set_tenant(branch.tenant)
        
        products = Product.objects.filter(branch=branch, is_active=True).values('id', 'stock_quantity')
        
        return Response(list(products))
        return Response(list(products))

class KioskViewSet(viewsets.ViewSet):
    """
    Dedicated ViewSet for Kiosk operations (Unauthenticated).
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @action(detail=False, methods=['get'], url_path='data/(?P<branch_id>[^/.]+)')
    def data(self, request, branch_id=None):
        from django.shortcuts import get_object_or_404
        from accounts.models import Branch
        from main.models import Product, Customer, Category
        from django.utils import timezone
        from branches.api_serializers import ProductSerializer, CategorySerializer, CustomerSerializer
        from django_tenants.utils import schema_context
        from django.db import connection

        branch = get_object_or_404(Branch, pk=branch_id)
        
        with schema_context(branch.tenant.schema_name):
            products = Product.objects.filter(branch=branch, is_active=True)
            products_data = ProductSerializer(products, many=True).data
            
            categories = Category.objects.filter(branch=branch)
            categories_data = CategorySerializer(categories, many=True).data
            
            customers = Customer.objects.filter(tenant=branch.tenant)
            customers_data = CustomerSerializer(customers, many=True).data
            
            return Response({
                'products': products_data,
                'categories': categories_data,
                'customers': customers_data,
                'timestamp': timezone.now(),
                'server_schema': connection.get_schema(),
                'products_count': len(products_data),
            })

    @action(detail=False, methods=['post'], url_path='transaction')
    def transaction(self, request):
        from django.shortcuts import get_object_or_404
        from accounts.models import Branch, UserProfile
        from branches.services.pos import POSService
        from django_tenants.utils import schema_context
        
        data = request.data
        branch_id = data.get('data', {}).get('branch_id')
        
        if not branch_id:
            # Fallback for some payloads?
             branch_id = data.get('branch_id')

        if not branch_id:
             return Response({'error': 'Branch ID required'}, status=status.HTTP_400_BAD_REQUEST)
             
        branch = get_object_or_404(Branch, pk=branch_id)
        
        # Manually set tenant for the request context (needed by POSService possibly)
        request.tenant = branch.tenant 

        with schema_context(branch.tenant.schema_name):
            uuid = data.get('uuid')
            transaction_type = data.get('type')
            transaction_data = data.get('data')
            
            if transaction_type == 'order':
                 # Kiosk orders don't have a cashier usually, or use a system user
                 # specific logic for Kiosk order might be needed in POSService
                 # For now passing user_profile=None
                 pos_service = POSService(tenant=branch.tenant, user_profile=None)
                 result = pos_service.sync_order(uuid, transaction_data)
                 
                 if result['status'] == 'success':
                    return Response({
                        'status': 'success', 
                        'id': str(result['order_id']),
                        'order_number': result.get('order_number')
                    }, status=status.HTTP_201_CREATED)
                 else:
                    return Response({'error': result.get('message', 'Unknown error')}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'error': 'Invalid transaction type'}, status=status.HTTP_400_BAD_REQUEST)
