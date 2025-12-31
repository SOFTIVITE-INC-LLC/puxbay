# Puxbay Ruby SDK

Official Ruby SDK for the Puxbay POS API.

## Features

- ✅ Complete API coverage (25+ endpoints)
- ✅ Idiomatic Ruby with method chaining
- ✅ Faraday HTTP client with middleware
- ✅ Automatic retry with exponential backoff
- ✅ Connection pooling
- ✅ Hash-based responses
- ✅ Ruby 2.6+ compatible

## Installation

Add this line to your application's Gemfile:

```ruby
gem 'puxbay'
```

And then execute:

```bash
bundle install
```

Or install it yourself as:

```bash
gem install puxbay
```

## Quick Start

```ruby
require 'puxbay'

# Configure globally
Puxbay.configure do |config|
  config.api_key = 'pb_your_api_key_here'
  config.max_retries = 5
  config.timeout = 30
end

# Or create a client instance
client = Puxbay::Client.new('pb_your_api_key_here')

# List products
products = client.products.list(page: 1, page_size: 20)
products['results'].each do |product|
  puts "#{product['name']}: $#{product['price']}"
end

# Create a new product
new_product = {
  name: 'New Product',
  sku: 'SKU-001',
  price: 29.99,
  stock_quantity: 100,
  category: 'category-id'
}

created = client.products.create(new_product)
```

## Configuration Options

```ruby
client = Puxbay::Client.new('pb_your_api_key', {
  base_url: 'https://api.puxbay.com/api/v1',  # Custom base URL
  timeout: 30,                                  # Request timeout (seconds)
  max_retries: 3,                              # Max retry attempts
  open_timeout: 10,                            # Connection timeout
  pool_size: 10                                # Connection pool size
})
```

## API Resources

### Products
```ruby
# List products
products = client.products.list(page: 1, page_size: 20)

# Get product
product = client.products.get('product-id')

# Create product
created = client.products.create(new_product)

# Update product
updated = client.products.update('product-id', product)

# Delete product
client.products.delete('product-id')

# Adjust stock
client.products.adjust_stock('product-id', quantity: 10, reason: 'Added inventory')
```

### Orders
```ruby
# List orders
orders = client.orders.list(page: 1, page_size: 20)

# Get order
order = client.orders.get('order-id')

# Create order
created = client.orders.create(new_order)

# Cancel order
cancelled = client.orders.cancel('order-id')
```

### Customers
```ruby
# List customers
customers = client.customers.list(page: 1, page_size: 20)

# Get customer
customer = client.customers.get('customer-id')

# Create customer
created = client.customers.create(new_customer)

# Update customer
updated = client.customers.update('customer-id', customer)

# Adjust loyalty points
adjusted = client.customers.adjust_loyalty_points('customer-id', 
  points: 100, 
  description: 'Bonus points'
)
```

### All Resources

- `client.products` - Product management
- `client.orders` - Order management
- `client.customers` - Customer management
- `client.inventory` - Inventory tracking
- `client.reports` - Sales reports & analytics
- `client.categories` - Product categories
- `client.suppliers` - Supplier management
- `client.purchase_orders` - Purchase orders
- `client.stock_transfers` - Stock transfers
- `client.stocktakes` - Stocktake sessions
- `client.cash_drawers` - Cash drawer management
- `client.gift_cards` - Gift card operations
- `client.expenses` - Expense tracking
- `client.branches` - Branch management
- `client.staff` - Staff management
- `client.webhooks` - Webhook configuration
- `client.notifications` - Notifications
- `client.returns` - Return processing

## Error Handling

```ruby
begin
  product = client.products.get('invalid-id')
rescue Puxbay::NotFoundError => e
  puts "Product not found: #{e.message}"
rescue Puxbay::AuthenticationError => e
  puts "Invalid API key: #{e.message}"
rescue Puxbay::RateLimitError => e
  puts "Rate limit exceeded: #{e.message}"
rescue Puxbay::ValidationError => e
  puts "Validation error: #{e.message}"
rescue Puxbay::ServerError => e
  puts "Server error: #{e.message}"
rescue Puxbay::Error => e
  puts "API error: #{e.message}"
  puts "Status code: #{e.status_code}"
end
```

## Development

After checking out the repo, run `bin/setup` to install dependencies. Then, run `rake spec` to run the tests.

```bash
git clone https://github.com/puxbay/puxbay-ruby.git
cd puxbay-ruby
bundle install
rake spec
```

## Requirements

- Ruby 2.6 or higher

## Dependencies

- faraday ~> 2.7 - HTTP client
- faraday-retry ~> 2.2 - Retry middleware
- json ~> 2.6 - JSON parsing

## License

MIT License - see LICENSE file for details

## Support

- Documentation: https://docs.puxbay.com
- API Reference: https://api.puxbay.com/docs
- Issues: https://github.com/puxbay/puxbay-ruby/issues
- Email: support@puxbay.com
