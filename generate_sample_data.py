import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from branches.xlsx_utils import XLSXGenerator

# Sample data pools
categories = [
    'Beverages', 'Snacks', 'Dairy Products', 'Bakery', 'Canned Goods',
    'Frozen Foods', 'Fresh Produce', 'Meat & Poultry', 'Seafood', 'Condiments',
    'Cereals', 'Pasta & Rice', 'Cooking Oil', 'Spices', 'Personal Care',
    'Household Cleaning', 'Health & Wellness', 'Baby Products', 'Pet Food', 'Electronics'
]

product_prefixes = {
    'Beverages': ['Coca Cola', 'Pepsi', 'Fanta', 'Sprite', 'Mountain Dew', 'Dr Pepper', 'Juice', 'Water', 'Energy Drink', 'Tea'],
    'Snacks': ['Chips', 'Crackers', 'Cookies', 'Pretzels', 'Popcorn', 'Nuts', 'Candy Bar', 'Gum', 'Chocolate', 'Trail Mix'],
    'Dairy Products': ['Milk', 'Cheese', 'Yogurt', 'Butter', 'Cream', 'Ice Cream', 'Sour Cream', 'Cottage Cheese'],
    'Bakery': ['Bread', 'Rolls', 'Bagels', 'Muffins', 'Donuts', 'Croissants', 'Cake', 'Pastry'],
    'Canned Goods': ['Soup', 'Beans', 'Tomatoes', 'Corn', 'Tuna', 'Vegetables', 'Fruit', 'Sauce'],
    'Frozen Foods': ['Pizza', 'Ice Cream', 'Vegetables', 'Meals', 'Chicken Nuggets', 'French Fries', 'Waffles'],
    'Fresh Produce': ['Apples', 'Bananas', 'Oranges', 'Tomatoes', 'Lettuce', 'Carrots', 'Potatoes', 'Onions'],
    'Meat & Poultry': ['Chicken Breast', 'Ground Beef', 'Pork Chops', 'Bacon', 'Sausage', 'Turkey', 'Ham'],
    'Seafood': ['Salmon', 'Shrimp', 'Tuna', 'Cod', 'Tilapia', 'Crab', 'Lobster'],
    'Condiments': ['Ketchup', 'Mustard', 'Mayonnaise', 'Hot Sauce', 'BBQ Sauce', 'Soy Sauce', 'Vinegar'],
    'Cereals': ['Corn Flakes', 'Cheerios', 'Oatmeal', 'Granola', 'Rice Krispies', 'Frosted Flakes'],
    'Pasta & Rice': ['Spaghetti', 'Penne', 'Rice', 'Macaroni', 'Lasagna', 'Noodles'],
    'Cooking Oil': ['Vegetable Oil', 'Olive Oil', 'Canola Oil', 'Coconut Oil', 'Sunflower Oil'],
    'Spices': ['Salt', 'Pepper', 'Garlic Powder', 'Paprika', 'Cumin', 'Oregano', 'Basil'],
    'Personal Care': ['Shampoo', 'Soap', 'Toothpaste', 'Deodorant', 'Lotion', 'Razor', 'Shaving Cream'],
    'Household Cleaning': ['Dish Soap', 'Laundry Detergent', 'Bleach', 'All-Purpose Cleaner', 'Paper Towels'],
    'Health & Wellness': ['Vitamins', 'Pain Reliever', 'Bandages', 'Cough Syrup', 'Antacid'],
    'Baby Products': ['Diapers', 'Baby Food', 'Baby Wipes', 'Formula', 'Baby Lotion'],
    'Pet Food': ['Dog Food', 'Cat Food', 'Bird Seed', 'Fish Food', 'Pet Treats'],
    'Electronics': ['Batteries', 'Charger', 'Headphones', 'USB Cable', 'Power Bank']
}

sizes = ['Small', 'Medium', 'Large', 'XL', '500ml', '1L', '2L', '250g', '500g', '1kg', '2kg', '100g', '200g']
brands = ['Premium', 'Value', 'Organic', 'Fresh', 'Classic', 'Deluxe', 'Select', 'Choice', 'Quality', 'Best']

countries = ['USA', 'UK', 'China', 'Germany', 'France', 'Italy', 'Japan', 'Canada', 'Australia', 'Ghana', 'Nigeria', 'South Africa']

def generate_sku(category, index):
    """Generate a unique SKU"""
    cat_code = category[:3].upper()
    return f"{cat_code}{index:04d}"

def generate_barcode():
    """Generate a random 13-digit barcode"""
    return ''.join([str(random.randint(0, 9)) for _ in range(13)])

def generate_expiry_date():
    """Generate a random expiry date 30-365 days in the future"""
    if random.random() < 0.3:  # 30% chance of no expiry
        return ''
    days = random.randint(30, 365)
    expiry = datetime.now() + timedelta(days=days)
    return expiry.strftime('%Y-%m-%d')

def generate_mfg_date():
    """Generate a random manufacturing date 1-180 days in the past"""
    if random.random() < 0.5:  # 50% chance of no mfg date
        return ''
    days = random.randint(1, 180)
    mfg = datetime.now() - timedelta(days=days)
    return mfg.strftime('%Y-%m-%d')

def create_large_sample(num_products=300):
    """Create a large sample XLSX file with many products"""
    generator = XLSXGenerator()
    
    # Headers
    headers = [
        'Product Name', 'SKU', 'Category', 'Price', 'Wholesale Price',
        'Min Wholesale Qty', 'Cost Price', 'Stock Quantity', 'Low Stock Threshold',
        'Barcode', 'Expiry Date', 'Batch Number', 'Invoice/Waybill',
        'Description', 'Active', 'Image URL', 'Manufacturing Date',
        'Country of Origin', 'Manufacturer Name', 'Manufacturer Address'
    ]
    generator.writerow(headers)
    
    print(f"Generating {num_products} sample products...")
    
    product_index = 1
    for i in range(num_products):
        # Select random category
        category = random.choice(categories)
        
        # Get product prefix for this category
        prefixes = product_prefixes.get(category, ['Product'])
        prefix = random.choice(prefixes)
        
        # Generate product name
        size = random.choice(sizes) if random.random() < 0.6 else ''
        brand = random.choice(brands) if random.random() < 0.4 else ''
        
        name_parts = [part for part in [brand, prefix, size] if part]
        product_name = ' '.join(name_parts)
        
        # Generate SKU
        sku = generate_sku(category, product_index)
        product_index += 1
        
        # Generate prices
        base_price = round(random.uniform(2.0, 150.0), 2)
        cost_price = round(base_price * random.uniform(0.5, 0.7), 2)
        wholesale_price = round(base_price * random.uniform(0.85, 0.95), 2)
        
        # Generate stock quantities
        stock_qty = random.randint(0, 500)
        low_stock_threshold = random.randint(5, 30)
        min_wholesale_qty = random.choice([6, 12, 24, 48])
        
        # Generate other fields
        barcode = generate_barcode()
        expiry_date = generate_expiry_date()
        batch_number = f"BATCH{random.randint(1000, 9999)}" if random.random() < 0.5 else ''
        invoice = f"INV-{random.randint(1000, 9999)}" if random.random() < 0.3 else ''
        
        description = f"High quality {product_name.lower()} for your daily needs"
        active = random.choice(['TRUE', 'TRUE', 'TRUE', 'FALSE'])  # 75% active
        
        # Manufacturing info
        mfg_date = generate_mfg_date()
        country = random.choice(countries)
        mfg_name = f"{random.choice(brands)} Manufacturing Co."
        mfg_address = f"{random.randint(100, 999)} Industrial Ave, {country}"
        
        # Create row
        row = [
            product_name, sku, category, base_price, wholesale_price,
            min_wholesale_qty, cost_price, stock_qty, low_stock_threshold,
            barcode, expiry_date, batch_number, invoice,
            description, active, '', mfg_date,
            country, mfg_name, mfg_address
        ]
        
        generator.writerow(row)
        
        if (i + 1) % 50 == 0:
            print(f"  Generated {i + 1} products...")
    
    print(f"✓ Generated all {num_products} products")
    return generator.generate()

def main():
    print("Creating large sample XLSX file with 300 products...")
    xlsx_bytes = create_large_sample(300)
    
    # Save to file
    filename = 'sample_products_300.xlsx'
    with open(filename, 'wb') as f:
        f.write(xlsx_bytes)
    
    file_size_kb = len(xlsx_bytes) / 1024
    print(f"\n✓ Created {filename} ({file_size_kb:.1f} KB)")
    print(f"✓ File location: {os.path.abspath(filename)}")
    print(f"\nYou can now upload this file through the web interface to test the import!")

if __name__ == "__main__":
    main()
