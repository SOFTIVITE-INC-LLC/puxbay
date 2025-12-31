# Puxbay Python SDK

Official Python client library for the Puxbay POS API.

## Installation

```bash
pip install puxbay
```

## Quick Start

```python
from puxbay import Puxbay

# Initialize the client
client = Puxbay(api_key="pb_your_api_key_here")

# List products
products = client.products.list(page=1, page_size=20)
print(f"Found {len(products['results'])} products")

# Create a customer
customer = client.customers.create({
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
})

# Create an order
order = client.orders.create({
    "customer": customer['id'],
    "items": [
        {"product": "product-uuid", "quantity": 2, "price": 29.99}
    ],
    "payment_method": "cash",
    "status": "completed"
})

# Get sales report
report = client.reports.sales_summary(
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

## Authentication

Get your API key from the Developer Settings in your Puxbay dashboard:
1. Navigate to Settings → Developer Settings
2. Click "Create API Key"
3. Copy your key (starts with `pb_`)

## Available Resources

### Products
```python
# List products
products = client.products.list(search="laptop")

# Get a product
product = client.products.get("product-uuid")

# Create a product
product = client.products.create({
    "name": "Laptop",
    "sku": "LAP-001",
    "price": 999.99,
    "category": "category-uuid"
})

# Update a product
product = client.products.update("product-uuid", {"price": 899.99})

# Adjust stock
product = client.products.adjust_stock("product-uuid", quantity=10)
```

### Orders
```python
# List orders
orders = client.orders.list(status="completed")

# Get an order
order = client.orders.get("order-uuid")

# Create an order
order = client.orders.create({
    "customer": "customer-uuid",
    "items": [{"product": "product-uuid", "quantity": 1, "price": 99.99}]
})

# Cancel an order
order = client.orders.cancel("order-uuid", reason="Customer request")
```

### Customers
```python
# List customers
customers = client.customers.list(search="john")

# Get a customer
customer = client.customers.get("customer-uuid")

# Add loyalty points
customer = client.customers.add_loyalty_points("customer-uuid", points=100)

# Add store credit
customer = client.customers.add_store_credit("customer-uuid", amount=50.00)
```

### Inventory
```python
# Get stock levels
stock = client.inventory.get_stock_levels()

# Get low stock items
low_stock = client.inventory.get_low_stock(threshold=10)

# Create stock transfer
transfer = client.inventory.create_transfer({
    "from_branch": "branch-uuid-1",
    "to_branch": "branch-uuid-2",
    "items": [{"product": "product-uuid", "quantity": 10}]
})
```

### Reports
```python
# Sales summary
sales = client.reports.sales_summary(
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Product performance
performance = client.reports.product_performance(limit=10)

# Customer analytics
analytics = client.reports.customer_analytics()

# Profit & loss
pl = client.reports.profit_loss(
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

## Error Handling

```python
from puxbay import Puxbay, AuthenticationError, RateLimitError, ValidationError

client = Puxbay(api_key="pb_your_key")

try:
    product = client.products.get("invalid-uuid")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded, please retry later")
except ValidationError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Configuration

```python
# Custom base URL (for testing or self-hosted)
client = Puxbay(
    api_key="pb_your_key",
    base_url="https://your-domain.com/api/v1",
    timeout=60  # Request timeout in seconds
)
```

## Support

- Documentation: https://docs.puxbay.com
- API Reference: https://api.puxbay.com/docs
- Issues: https://github.com/puxbay/puxbay-python/issues

## License

MIT License - see LICENSE file for details
