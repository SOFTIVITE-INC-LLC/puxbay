from decimal import Decimal
from django.db import models
from django.db.models import Sum, Count, Q
from django.utils import timezone
from main.models import Product, Order, Supplier
from branches.models import PurchaseOrder, PurchaseOrderItem
import uuid

class IntelligenceService:
    def __init__(self, tenant, branch=None):
        self.tenant = tenant
        self.branch = branch

    def generate_auto_pos(self, user_profile):
        """
        Scans products with auto_reorder=True that are below low_stock_threshold.
        Groups them by supplier and creates Draft Purchase Orders.
        """
        products_to_reorder = Product.objects.filter(
            tenant=self.tenant,
            auto_reorder=True,
            is_active=True,
            supplier__isnull=False
        ).filter(stock_quantity__lte=models.F('low_stock_threshold'))

        if self.branch:
            products_to_reorder = products_to_reorder.filter(branch=self.branch)

        # Group by supplier
        supplier_map = {}
        for p in products_to_reorder:
            if p.supplier_id not in supplier_map:
                supplier_map[p.supplier_id] = []
            supplier_map[p.supplier_id].append(p)

        orders_created = []
        for supplier_id, products in supplier_map.items():
            supplier = Supplier.objects.get(id=supplier_id)
            
            # Generate PO number
            po_number = f"PO-{uuid.uuid4().hex[:8].upper()}"
            
            # Use branch-level PurchaseOrder
            po = PurchaseOrder.objects.create(
                tenant=self.tenant,
                branch=self.branch or products[0].branch,
                supplier=supplier,
                reference_id=po_number,
                status='draft',
                created_by=user_profile
            )
            
            total_cost = Decimal('0.00')
            for p in products:
                qty = p.reorder_quantity or 10
                unit_cost = p.cost_price or Decimal('0.00')
                
                PurchaseOrderItem.objects.create(
                    po=po,
                    product=p,
                    quantity=qty,
                    unit_cost=unit_cost
                )
                total_cost += (qty * unit_cost)
            
            po.total_cost = total_cost
            po.save()
            orders_created.append(po)

        return orders_created

    def get_frequently_bought_together(self, product, limit=4):
        """
        Analyzes order history to find products frequently purchased with the given product.
        Simple co-occurrence logic.
        """
        from main.models import OrderItem
        
        # Get IDs of orders containing this product
        order_ids = OrderItem.objects.filter(
            product=product,
            order__status='completed'
        ).values_list('order_id', flat=True).order_by('-order__created_at')[:1000]

        if not order_ids:
            return []

        # Find other products in those same orders
        related_products = OrderItem.objects.filter(
            order_id__in=order_ids
        ).exclude(
            product=product
        ).values('product_id').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]

        if not related_products:
            return []

        # Fetch full product objects
        product_ids = [item['product_id'] for item in related_products]
        # Preserve order from co-occurrence count
        preserved_order = models.Case(*[models.When(pk=pk, then=pos) for pos, pk in enumerate(product_ids)])
        return Product.objects.filter(id__in=product_ids).order_by(preserved_order)
