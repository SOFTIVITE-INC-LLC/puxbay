"""
Barcode Service for generating and managing product barcodes.
Supports multiple barcode formats including EAN-13, Code128, and QR codes.
"""
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile
import random
import string


def generate_barcode_number(product):
    """
    Generate a unique barcode number for a product.
    Uses EAN-13 format (13 digits).
    
    Args:
        product: Product instance
    
    Returns:
        String of 13 digits
    """
    if product.barcode:
        return product.barcode
    
    # Generate 12 random digits (13th is check digit, auto-calculated)
    # Format: Country(3) + Manufacturer(4) + Product(5)
    country_code = '001'  # Custom country code
    manufacturer = str(product.tenant.id)[:4].zfill(4)
    product_code = str(product.id)[:5].replace('-', '')[:5].zfill(5)
    
    barcode_base = country_code + manufacturer + product_code
    
    # Calculate EAN-13 check digit
    odd_sum = sum(int(barcode_base[i]) for i in range(0, 12, 2))
    even_sum = sum(int(barcode_base[i]) for i in range(1, 12, 2))
    check_digit = (10 - ((odd_sum + even_sum * 3) % 10)) % 10
    
    return barcode_base + str(check_digit)


def generate_barcode_image(barcode_number, format='ean13'):
    """
    Generate barcode image from barcode number.
    
    Args:
        barcode_number: Barcode number string
        format: Barcode format ('ean13', 'code128', etc.)
    
    Returns:
        BytesIO object containing PNG image
    """
    try:
        # Get barcode class
        barcode_class = barcode.get_barcode_class(format)
        
        # Generate barcode
        barcode_instance = barcode_class(barcode_number, writer=ImageWriter())
        
        # Save to BytesIO
        buffer = BytesIO()
        barcode_instance.write(buffer, options={
            'module_width': 0.3,
            'module_height': 15.0,
            'quiet_zone': 6.5,
            'font_size': 10,
            'text_distance': 5.0,
        })
        buffer.seek(0)
        
        return buffer
    except Exception as e:
        print(f"Error generating barcode: {e}")
        return None


def create_product_barcode(product, save=True):
    """
    Create and optionally save barcode for a product.
    
    Args:
        product: Product instance
        save: Whether to save the product after generating barcode
    
    Returns:
        Product instance with barcode
    """
    if not product.barcode:
        # Generate barcode number
        barcode_number = generate_barcode_number(product)
        product.barcode = barcode_number
        
        if save:
            product.save()
    
    return product


def generate_receipt_barcode(order_number):
    """
    Generate barcode for receipt/order tracking.
    Uses Code128 format for alphanumeric support.
    
    Args:
        order_number: Order number string
    
    Returns:
        BytesIO object containing PNG image
    """
    try:
        # Use Code128 for alphanumeric order numbers
        barcode_class = barcode.get_barcode_class('code128')
        barcode_instance = barcode_class(order_number, writer=ImageWriter())
        
        buffer = BytesIO()
        barcode_instance.write(buffer, options={
            'module_width': 0.2,
            'module_height': 10.0,
            'quiet_zone': 3.0,
            'font_size': 8,
            'text_distance': 3.0,
        })
        buffer.seek(0)
        
        return buffer
    except Exception as e:
        print(f"Error generating receipt barcode: {e}")
        return None


def bulk_generate_barcodes(products):
    """
    Generate barcodes for multiple products.
    
    Args:
        products: QuerySet or list of Product instances
    
    Returns:
        Dictionary with success count and errors
    """
    success_count = 0
    errors = []
    
    for product in products:
        try:
            if not product.barcode:
                create_product_barcode(product, save=True)
                success_count += 1
        except Exception as e:
            errors.append({
                'product': product.name,
                'error': str(e)
            })
    
    return {
        'success': success_count,
        'errors': errors,
        'total': len(products)
    }


def get_barcode_svg(barcode_number, format='ean13'):
    """
    Generate barcode as SVG (scalable vector graphics).
    
    Args:
        barcode_number: Barcode number string
        format: Barcode format
    
    Returns:
        SVG string
    """
    try:
        from barcode.writer import SVGWriter
        
        barcode_class = barcode.get_barcode_class(format)
        barcode_instance = barcode_class(barcode_number, writer=SVGWriter())
        
        buffer = BytesIO()
        barcode_instance.write(buffer)
        buffer.seek(0)
        
        return buffer.getvalue().decode('utf-8')
    except Exception as e:
        print(f"Error generating SVG barcode: {e}")
        return None
