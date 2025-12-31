from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from main.models import Product
from branches.models import StockMovement, InventoryRecommendation
from decimal import Decimal

class InventoryAIService:
    """
    Service to analyze stock trends and generate reorder recommendations.
    """
    def __init__(self, tenant):
        self.tenant = tenant

    def run_analysis(self, branch=None):
        """
        Runs the inventory analysis for a specific branch or all branches in the tenant.
        """
        if branch:
            return self._analyze_branch(branch)
        
        results = []
        for branch in self.tenant.branches.all():
            results.append(self._analyze_branch(branch))
        return results

    def _analyze_branch(self, branch):
        """
        Core logic for a single branch.
        """
        products = Product.objects.filter(branch=branch, tenant=self.tenant, is_active=True)
        recommendations_count = 0
        
        # Consider the last 30 days for velocity calculation
        lookback_days = 30
        since_date = timezone.now() - timedelta(days=lookback_days)

        for product in products:
            velocity = self._calculate_velocity(product, since_date, lookback_days)
            
            if velocity > 0:
                # Calculate estimated days remaining
                days_remaining = int(product.stock_quantity / velocity) if product.stock_quantity > 0 else 0
                
                # If we have less than 7 days of stock left, or we are already out
                if days_remaining <= 7:
                    # Recommend 14 days worth of stock
                    recommended_qty = int(velocity * 14)
                    
                    # Ensure minimum of 1 recommendation if velocity is high
                    if recommended_qty == 0 and velocity > 0:
                        recommended_qty = 1

                    InventoryRecommendation.objects.update_or_create(
                        branch=branch,
                        product=product,
                        defaults={
                            'tenant': self.tenant,
                            'predicted_velocity': velocity,
                            'current_stock': product.stock_quantity,
                            'estimated_days_left': days_remaining,
                            'recommended_reorder_quantity': recommended_qty,
                            'is_dismissed': False # Reset dismissal on re-analysis if still critical
                        }
                    )
                    recommendations_count += 1
            else:
                # If velocity is 0 and we have a recommendation, we might want to keep it or delete it.
                # For now, if no sales in 30 days, we remove the recommendation.
                InventoryRecommendation.objects.filter(branch=branch, product=product).delete()

        return {
            'branch': branch.name,
            'processed_count': products.count(),
            'recommendations_created': recommendations_count
        }

    def _calculate_velocity(self, product, since_date, days):
        """
        Calculates average daily sales for a product.
        """
        # Sum all 'sale' movements
        total_sales = StockMovement.objects.filter(
            product=product,
            movement_type='sale',
            created_at__gte=since_date
        ).aggregate(total=Sum('quantity_change'))['total'] or 0
        
        # quantity_change for sales is negative, so we use absolute value
        abs_sales = abs(total_sales)
        
        # Return average per day
        return Decimal(abs_sales) / Decimal(days)
