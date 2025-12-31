
import os
import sys
import random
from io import BytesIO

# Add current directory to path so we can import branches.xlsx_utils
sys.path.append(os.getcwd())

from branches.xlsx_utils import XLSXGenerator

def generate_150_products():
    print("Generating 150 test product entries...")
    generator = XLSXGenerator()
    
    headers = [
        'Name', 'SKU', 'Category', 'Price', 'Wholesale Price', 
        'Min Wholesale Qty', 'Cost Price', 'Stock Quantity', 'Low Stock Threshold', 
        'Barcode', 'Expiry Date (YYYY-MM-DD)', 'Batch Number', 'Invoice Number', 
        'Description', 'Is Active', 'Image URL'
    ]
    generator.writerow(headers)
    
    categories = ['Laptops', 'Smartphones', 'Audio', 'Accessories', 'Gaming', 'Monitors']
    
    image_pool = [
        'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800', # Laptop
        'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=800', # Laptop 2
        'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=800', # Phone
        'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800', # Phone 2
        'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800', # Audio
        'https://images.unsplash.com/photo-1588423770670-45731ff1f39b?w=800', # Audio 2
        'https://images.unsplash.com/photo-1589492477829-5e65395b66cc?w=800', # Accessory
        'https://images.unsplash.com/photo-1527443154391-507e9dc6c5cc?w=800', # Stand
        'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800', # Gaming
        'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800', # Monitor
    ]
    
    product_names = [
        "UltraBook Pro X", "SkyPhone 15", "EchoPods Max", "Gaming Gear Mouse", "Titan Monitor 27",
        "NexGen Processor", "Z-Series SSD 1TB", "PowerBank Ultra", "Mechanical Keyboard RGB", "NoiseCancel Elite",
        "StreamWeb Cam HD", "FastCharge Wall Plug", "Wireless Dongle Pro", "Leather Laptop Sleeve", "Ergo Chair Pro",
        "Smart Band V5", "Mini Drone 4K", "External HDD 2TB", "Dual Display Adapter", "Silent Click Mouse"
    ]

    for i in range(1, 151):
        name_prefix = random.choice(product_names)
        name = f"{name_prefix} - Model {100 + i}"
        sku = f"TEST-SKU-{1000 + i}"
        category = random.choice(categories)
        price = round(random.uniform(20.0, 2500.0), 2)
        wholesale_price = round(price * 0.85, 2)
        min_wholesale_qty = random.randint(5, 20)
        cost_price = round(wholesale_price * 0.7, 2)
        stock_qty = random.randint(0, 500)
        threshold = random.randint(5, 25)
        barcode = f"99{random.randint(100000, 999999)}"
        expiry = "2026-12-31" if i % 5 == 0 else ""
        batch = f"BATCH-{random.randint(200, 300)}"
        invoice = f"INV-TEST-{2025000 + i}"
        description = f"This is a high-quality test entry for {name}. Perfect for bulk import testing."
        is_active = "TRUE"
        image_url = random.choice(image_pool)
        
        row = [
            name, sku, category, price, wholesale_price, 
            min_wholesale_qty, cost_price, stock_qty, threshold, 
            barcode, expiry, batch, invoice, 
            description, is_active, image_url
        ]
        generator.writerow(row)
    
    # Write to file
    file_path = "import_test_150.xlsx"
    with open(file_path, "wb") as f:
        f.write(generator.generate())
    
    print(f"Successfully generated {file_path}")

if __name__ == "__main__":
    generate_150_products()
