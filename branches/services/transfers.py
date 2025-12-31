import uuid
import json
from django.db import transaction
from django.utils import timezone
from main.models import Product
from ..models import StockTransfer, StockTransferItem, StockMovement

class TransferService:
    def __init__(self, tenant, user_profile=None):
        self.tenant = tenant
        self.user_profile = user_profile

    def request_transfer(self, source_branch, destination_branch, items_data, notes=None):
        """
        Creates a new stock transfer request.
        items_data format: [{'product_id': UUID, 'quantity': int, 'transfer_price': float}]
        """
        with transaction.atomic():
            reference_id = f"TRF-{uuid.uuid4().hex[:8].upper()}"
            transfer = StockTransfer.objects.create(
                tenant=self.tenant,
                source_branch=source_branch,
                destination_branch=destination_branch,
                reference_id=reference_id,
                status='requested',
                created_by=self.user_profile,
                notes=notes
            )

            for item in items_data:
                product_id = item.get('product_id')
                if not product_id: continue
                
                # We expect the product_id to be the UID of the product in the SOURCE branch
                product = Product.objects.get(id=product_id, tenant=self.tenant)
                
                StockTransferItem.objects.create(
                    transfer=transfer,
                    product=product,
                    quantity=int(item['quantity']),
                    transfer_price=item.get('transfer_price')
                )
            
            return transfer

    def approve_transfer(self, transfer_id):
        """
        Approves a requested transfer.
        """
        try:
            transfer = StockTransfer.objects.get(id=transfer_id, tenant=self.tenant)
            if transfer.status != 'requested':
                return {'status': 'error', 'message': f'Cannot approve transfer in {transfer.status} state.'}
            
            transfer.status = 'approved'
            transfer.save()
            return {'status': 'success', 'transfer': transfer}
        except StockTransfer.DoesNotExist:
            return {'status': 'error', 'message': 'Transfer not found.'}

    def ship_transfer(self, transfer_id):
        """
        Marks a transfer as shipped and deducts stock from the source branch.
        """
        try:
            with transaction.atomic():
                transfer = StockTransfer.objects.select_for_update().get(id=transfer_id, tenant=self.tenant)
                if transfer.status != 'approved':
                    return {'status': 'error', 'message': f'Transfer must be approved before shipping (Status: {transfer.status}).'}

                # Deduct stock and record movement
                for item in transfer.items.all():
                    source_product = item.product
                    
                    if source_product.stock_quantity < item.quantity:
                        raise Exception(f"Insufficient stock for {source_product.name} at {transfer.source_branch.name}")

                    source_product.stock_quantity -= item.quantity
                    source_product.save()

                    StockMovement.objects.create(
                        tenant=self.tenant,
                        branch=transfer.source_branch,
                        product=source_product,
                        quantity_change=-item.quantity,
                        balance_after=source_product.stock_quantity,
                        movement_type='transfer_out',
                        reference=transfer.reference_id,
                        created_by=self.user_profile,
                        notes=f"Shipped to {transfer.destination_branch.name}"
                    )

                transfer.status = 'shipped'
                transfer.save()
                return {'status': 'success', 'transfer': transfer}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def receive_transfer(self, transfer_id):
        """
        Marks a transfer as completed and adds stock to the destination branch.
        """
        try:
            with transaction.atomic():
                transfer = StockTransfer.objects.select_for_update().get(id=transfer_id, tenant=self.tenant)
                if transfer.status != 'shipped':
                    return {'status': 'error', 'message': f'Cannot receive transfer. status: {transfer.status}. Must be shipped first.'}

                # Add stock and record movement
                for item in transfer.items.all():
                    # Find or create product in destination branch
                    dest_product = Product.objects.filter(
                        branch=transfer.destination_branch,
                        sku=item.product.sku,
                        tenant=self.tenant
                    ).first()

                    if not dest_product:
                        # Auto-create product in destination if it doesn't exist
                        # Note: In a production app, we might want a mapping or a more robust sync
                        source_p = item.product
                        dest_product = Product.objects.create(
                            tenant=self.tenant,
                            branch=transfer.destination_branch,
                            category=source_p.category, # Warning: Category might also be branch-tied
                            name=source_p.name,
                            sku=source_p.sku,
                            price=source_p.price,
                            stock_quantity=0,
                            description=source_p.description,
                            cost_price=item.transfer_price or source_p.cost_price,
                            is_active=True
                        )

                    dest_product.stock_quantity += item.quantity
                    dest_product.save()

                    StockMovement.objects.create(
                        tenant=self.tenant,
                        branch=transfer.destination_branch,
                        product=dest_product,
                        quantity_change=item.quantity,
                        balance_after=dest_product.stock_quantity,
                        movement_type='transfer_in',
                        reference=transfer.reference_id,
                        created_by=self.user_profile,
                        notes=f"Received from {transfer.source_branch.name}"
                    )

                transfer.status = 'completed'
                transfer.completed_at = timezone.now()
                transfer.save()
                return {'status': 'success', 'transfer': transfer}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
