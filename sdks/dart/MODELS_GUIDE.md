# Dart SDK Models Guide

## Overview

The Dart SDK includes **strongly-typed models** that strictly match the Puxbay API structure.

## Available Models

### Core Commerce
- **`Product`**, **`ProductVariant`**, **`ProductComponent`**
- **`Order`**, **`OrderItem`**
- **`Customer`**, **`CustomerTier`**
- **`Category`**
- **`Branch`**

### Supply Chain
- **`Supplier`**
- **`PurchaseOrder`**, **`PurchaseOrderItem`**
- **`StockTransfer`**, **`StockTransferItem`**
- **`StocktakeSession`**, **`StocktakeEntry`**

### Financial & Operations
- **`CashDrawerSession`**
- **`Expense`**, **`ExpenseCategory`**
- **`PaymentMethod`**
- **`TaxConfiguration`**
- **`Return`**, **`ReturnItem`**
- **`GiftCard`**

### CRM & Other
- **`Staff`**
- **`Notification`**
- **`CustomerFeedback`**
- **`LoyaltyTransaction`**
- **`StoreCreditTransaction`**
- **`PaginatedResponse<T>`**

## Usage Examples

### Using Typed Methods

```dart
import 'package:puxbay/puxbay.dart';

final client = Puxbay(apiKey: 'pb_your_key');

// Get typed paginated products
final PaginatedResponse<Product> products = await client.products.listTyped(
  page: 1,
  pageSize: 20,
);

print('Total products: ${products.count}');
for (final product in products.results) {
  print('${product.name}: \$${product.price}');
  
  // Access variants if available
  if (product.variants != null) {
    for (final variant in product.variants!) {
      print('  - ${variant.name}: ${variant.sku}');
    }
  }
}

// Get single typed product
final Product product = await client.products.getProductTyped('product-id');
```

### Working with Orders

```dart
// Orders have typed models for response parsing
final json = await client.orders.getOrder('order-id');
final order = Order.fromJson(json);

print('Order #${order.orderNumber}');
print('Customer: ${order.customerName}');
print('Total: \$${order.totalAmount}');

for (final item in order.items) {
  print('${item.quantity}x ${item.productName} @ \$${item.price}');
}
```

### Working with Customers & Loyalty

```dart
final json = await client.customers.getCustomer('customer-id');
final customer = Customer.fromJson(json);

print('Tier: ${customer.tierName}');
print('Loyalty Points: ${customer.loyaltyPoints}');
print('Store Credit: ${customer.storeCreditBalance}');
```

### Model Serialization

All models support standard `fromJson` / `toJson`:

```dart
// Serialize
final productJson = product.toJson();

// Deserialize
final product = Product.fromJson(apiResponse);
```

## Null Safety

All models strictly follow Dart's null safety. Fields that are optional in the API (like `description`, `email`, `metadata`) are nullable `String?` or `Map?` in dart.

```dart
if (product.description != null) {
  print(product.description);
}

// Using null-aware operators
print(customer.email?.toLowerCase() ?? 'no email');
```
