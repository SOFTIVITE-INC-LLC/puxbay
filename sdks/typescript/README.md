# @puxbay/sdk

Official TypeScript/JavaScript SDK for the Puxbay POS API.

## Installation

```bash
npm install @puxbay/sdk
# or
yarn add @puxbay/sdk
```

## Quick Start

```typescript
import { Puxbay } from '@puxbay/sdk';

// Initialize the client
const client = new Puxbay({
  apiKey: 'pb_your_api_key_here'
});

// List products
const products = await client.products.list({ page: 1, page_size: 20 });
console.log(`Found ${products.count} products`);

// Create a customer
const customer = await client.customers.create({
  name: 'John Doe',
  email: 'john@example.com',
  phone: '+1234567890'
});

// Create an order
const order = await client.orders.create({
  customer: customer.id,
  items: [
    { product: 'product-uuid', quantity: 2, price: 29.99 }
  ],
  payment_method: 'cash',
  status: 'completed'
});

// Get sales report
const report = await client.reports.salesSummary('2024-01-01', '2024-12-31');
```

## Authentication

Get your API key from the Developer Settings in your Puxbay dashboard.

## Available Resources

### Products

```typescript
// List products
const products = await client.products.list({ search: 'laptop' });

// Get a product
const product = await client.products.get('product-uuid');

// Create a product
const product = await client.products.create({
  name: 'Laptop',
  sku: 'LAP-001',
  price: 999.99,
  category: 'category-uuid'
});

// Update a product
const product = await client.products.update('product-uuid', { price: 899.99 });

// Adjust stock
const product = await client.products.adjustStock('product-uuid', 10);
```

### Orders

```typescript
// List orders
const orders = await client.orders.list({ status: 'completed' });

// Get an order
const order = await client.orders.get('order-uuid');

// Create an order
const order = await client.orders.create({
  customer: 'customer-uuid',
  items: [{ product: 'product-uuid', quantity: 1, price: 99.99 }]
});

// Cancel an order
const order = await client.orders.cancel('order-uuid', 'Customer request');
```

### Customers

```typescript
// List customers
const customers = await client.customers.list({ search: 'john' });

// Get a customer
const customer = await client.customers.get('customer-uuid');

// Add loyalty points
const customer = await client.customers.addLoyaltyPoints('customer-uuid', 100);

// Add store credit
const customer = await client.customers.addStoreCredit('customer-uuid', 50.00);
```

### Inventory

```typescript
// Get stock levels
const stock = await client.inventory.getStockLevels();

// Get low stock items
const lowStock = await client.inventory.getLowStock(10);

// Create stock transfer
const transfer = await client.inventory.createTransfer({
  from_branch: 'branch-uuid-1',
  to_branch: 'branch-uuid-2',
  items: [{ product: 'product-uuid', quantity: 10 }]
});
```

### Reports

```typescript
// Sales summary
const sales = await client.reports.salesSummary('2024-01-01', '2024-12-31');

// Product performance
const performance = await client.reports.productPerformance('2024-01-01', '2024-12-31', 10);

// Customer analytics
const analytics = await client.reports.customerAnalytics('2024-01-01', '2024-12-31');

// Profit & loss
const pl = await client.reports.profitLoss('2024-01-01', '2024-12-31');
```

## Error Handling

```typescript
import {
  AuthenticationError,
  RateLimitError,
  ValidationError,
  NotFoundError
} from '@puxbay/sdk';

try {
  const product = await client.products.get('invalid-uuid');
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.log('Invalid API key');
  } else if (error instanceof RateLimitError) {
    console.log('Rate limit exceeded');
  } else if (error instanceof ValidationError) {
    console.log(`Validation error: ${error.message}`);
  } else if (error instanceof NotFoundError) {
    console.log('Resource not found');
  } else {
    console.log(`Unexpected error: ${error}`);
  }
}
```

## Configuration

```typescript
const client = new Puxbay({
  apiKey: 'pb_your_key',
  baseURL: 'https://your-domain.com/api/v1',  // Optional
  timeout: 60000  // Optional, in milliseconds
});
```

## TypeScript Support

This SDK is written in TypeScript and includes full type definitions for all API models and responses.

```typescript
import { Product, Order, Customer } from '@puxbay/sdk';

const product: Product = await client.products.get('product-uuid');
const order: Order = await client.orders.create({ ... });
```

## Support

- Documentation: https://docs.puxbay.com
- API Reference: https://api.puxbay.com/docs
- Issues: https://github.com/puxbay/puxbay-typescript/issues

## License

MIT License
