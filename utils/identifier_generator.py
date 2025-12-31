"""
Utility functions for generating unique identifiers for models.
These identifiers are human-readable and encrypted in the database.
"""
from django.db import transaction
from django.db.models import Max
import re


def generate_branch_id(tenant):
    """
    Generate a unique branch ID in format: BR-XXXX
    Example: BR-0001, BR-0002, etc.
    """
    from accounts.models import Branch
    
    with transaction.atomic():
        # Get the highest existing branch ID for this tenant
        existing_branches = Branch.objects.filter(
            tenant=tenant,
            unique_id__isnull=False
        ).select_for_update()
        
        # Extract numbers from existing IDs
        max_number = 0
        for branch in existing_branches:
            if branch.unique_id:
                match = re.search(r'BR-(\d+)', branch.unique_id)
                if match:
                    number = int(match.group(1))
                    max_number = max(max_number, number)
        
        # Generate next ID
        next_number = max_number + 1
        unique_id = f"BR-{next_number:04d}"
        
        # Ensure uniqueness (collision check)
        retry_count = 0
        while Branch.objects.filter(unique_id=unique_id).exists() and retry_count < 100:
            next_number += 1
            unique_id = f"BR-{next_number:04d}"
            retry_count += 1
        
        return unique_id


def generate_order_number(tenant):
    """
    Generate a unique order number in format: ORD-XXXXXX
    Example: ORD-000001, ORD-000123, etc.
    """
    from main.models import Order
    
    with transaction.atomic():
        # Get the highest existing order number for this tenant
        existing_orders = Order.objects.filter(
            tenant=tenant,
            order_number__isnull=False
        ).select_for_update()
        
        # Extract numbers from existing order numbers
        max_number = 0
        for order in existing_orders:
            if order.order_number:
                match = re.search(r'ORD-(\d+)', order.order_number)
                if match:
                    number = int(match.group(1))
                    max_number = max(max_number, number)
        
        # Generate next number
        next_number = max_number + 1
        order_number = f"ORD-{next_number:06d}"
        
        # Ensure uniqueness (collision check)
        retry_count = 0
        while Order.objects.filter(order_number=order_number).exists() and retry_count < 100:
            next_number += 1
            order_number = f"ORD-{next_number:06d}"
            retry_count += 1
        
        return order_number


def generate_item_number(order):
    """
    Generate a unique item number in format: ITM-XXXXX
    Example: ITM-00001, ITM-00456, etc.
    """
    from main.models import OrderItem
    
    with transaction.atomic():
        # Get the highest existing item number globally
        existing_items = OrderItem.objects.filter(
            item_number__isnull=False
        ).select_for_update()
        
        # Extract numbers from existing item numbers
        max_number = 0
        for item in existing_items:
            if item.item_number:
                match = re.search(r'ITM-(\d+)', item.item_number)
                if match:
                    number = int(match.group(1))
                    max_number = max(max_number, number)
        
        # Generate next number
        next_number = max_number + 1
        item_number = f"ITM-{next_number:05d}"
        
        # Ensure uniqueness (collision check)
        retry_count = 0
        while OrderItem.objects.filter(item_number=item_number).exists() and retry_count < 100:
            next_number += 1
            item_number = f"ITM-{next_number:05d}"
            retry_count += 1
        
        return item_number
