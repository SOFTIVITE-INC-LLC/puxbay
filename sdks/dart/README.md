# Puxbay Dart SDK

Official Dart/Flutter SDK for the Puxbay POS API.

[![pub package](https://img.shields.io/pub/v/puxbay.svg)](https://pub.dev/packages/puxbay)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- ✅ **Complete API Coverage** - All 18 resources with 50+ methods
- ✅ **Type-Safe** - Strongly typed responses and requests
- ✅ **Automatic Retry** - Exponential backoff for failed requests
- ✅ **Error Handling** - Comprehensive exception hierarchy
- ✅ **Flutter Ready** - Works seamlessly with Flutter apps
- ✅ **Null Safety** - Full null safety support
- ✅ **Testable** - Easy to mock and test
- ✅ **Production Ready** - Battle-tested and optimized

## Installation

Add this to your package's `pubspec.yaml` file:

```yaml
dependencies:
  puxbay: ^1.0.0
```

Then run:

```bash
dart pub get
```

Or with Flutter:

```bash
flutter pub get
```

## Quick Start

```dart
import 'package:puxbay/puxbay.dart';

void main() async {
  // Create client
  final client = Puxbay(
    apiKey: 'pb_your_api_key_here',
    config: PuxbayConfig(
      timeout: Duration(seconds: 30),
      maxRetries: 3,
    ),
  );

  try {
    // List products
    final products = await client.products.list(page: 1, pageSize: 20);
    print('Found ${products['count']} products');

    // Create an order
    final order = await client.orders.create({
      'customer': 'customer-id',
      'items': [
        {'product': 'product-id', 'quantity': 2},
      ],
    });
    print('Order created: ${order['id']}');

    // Get financial summary
    final summary = await client.reports.financialSummary(
      '2024-01-01',
      '2024-12-31',
    );
    print('Total sales: \$${summary['total_sales']}');
  } on AuthenticationException catch (e) {
    print('Authentication failed: ${e.message}');
  } on ValidationException catch (e) {
    print('Validation error: ${e.message}');
  } on PuxbayException catch (e) {
    print('API error: ${e.message}');
  } finally {
    client.close();
  }
}
```

## Configuration

```dart
final config = PuxbayConfig(
  baseUrl: 'https://api.puxbay.com/api/v1',  // Custom base URL
  timeout: Duration(seconds: 30),             // Request timeout
  maxRetries: 3,                              // Max retry attempts
  retryDelay: Duration(seconds: 1),           // Initial retry delay
  enableLogging: false,                       // Enable debug logging
);

final client = Puxbay(apiKey: 'pb_your_key', config: config);
```

## API Resources

### Products

```dart
// List products
final products = await client.products.list(page: 1, pageSize: 20);

// Get product
final product = await client.products.getProduct('product-id');

// Create product
final newProduct = await client.products.create({
  'name': 'New Product',
  'sku': 'SKU-001',
  'price': 29.99,
  'stock_quantity': 100,
});

// Update product
final updated = await client.products.update('product-id', {
  'price': 24.99,
});

// Delete product
await client.products.deleteProduct('product-id');

// Adjust stock
final adjusted = await client.products.adjustStock(
  'product-id',
  quantity: 10,
  reason: 'Restocked',
);

// Get history
final history = await client.products.history('product-id', page: 1);
```

### Orders

```dart
// List orders
final orders = await client.orders.list(page: 1, pageSize: 20);

// Get order
final order = await client.orders.getOrder('order-id');

// Create order
final newOrder = await client.orders.create({
  'customer': 'customer-id',
  'items': [...],
});

// Cancel order
final cancelled = await client.orders.cancel('order-id');
```

### Customers

```dart
// List customers
final customers = await client.customers.list(page: 1, pageSize: 20);

// Get customer
final customer = await client.customers.getCustomer('customer-id');

// Create customer
final newCustomer = await client.customers.create({
  'name': 'John Doe',
  'email': 'john@example.com',
});

// Update customer
final updated = await client.customers.update('customer-id', {...});

// Delete customer
await client.customers.deleteCustomer('customer-id');

// Adjust loyalty points
final adjusted = await client.customers.adjustLoyaltyPoints(
  'customer-id',
  points: 100,
  description: 'Bonus points',
);

// Adjust store credit
final credit = await client.customers.adjustStoreCredit(
  'customer-id',
  amount: 50.0,
  reference: 'Refund',
);
```

### All Available Resources

- `client.products` - Product management
- `client.orders` - Order management
- `client.customers` - Customer management
- `client.categories` - Product categories
- `client.suppliers` - Supplier management
- `client.giftCards` - Gift card operations
- `client.branches` - Branch management
- `client.staff` - Staff management
- `client.webhooks` - Webhook configuration
- `client.inventory` - Inventory tracking
- `client.reports` - Sales reports & analytics
- `client.purchaseOrders` - Purchase orders
- `client.stockTransfers` - Stock transfers
- `client.stocktakes` - Stocktake sessions
- `client.cashDrawers` - Cash drawer management
- `client.expenses` - Expense tracking
- `client.notifications` - Notifications
- `client.returns` - Return processing

## Error Handling

The SDK provides specific exception types for different error scenarios:

```dart
try {
  final product = await client.products.getProduct('invalid-id');
} on AuthenticationException catch (e) {
  // Handle 401 errors
  print('Invalid API key: ${e.message}');
} on RateLimitException catch (e) {
  // Handle 429 errors
  print('Rate limit exceeded: ${e.message}');
} on ValidationException catch (e) {
  // Handle 400 errors
  print('Validation failed: ${e.message}');
} on NotFoundException catch (e) {
  // Handle 404 errors
  print('Resource not found: ${e.message}');
} on ServerException catch (e) {
  // Handle 5xx errors
  print('Server error: ${e.message}');
} on NetworkException catch (e) {
  // Handle network errors
  print('Network error: ${e.message}');
} on PuxbayException catch (e) {
  // Handle all other API errors
  print('API error (${e.statusCode}): ${e.message}');
}
```

## Testing

The SDK is designed to be easily testable. You can mock the HTTP client:

```dart
import 'package:mockito/mockito.dart';
import 'package:http/http.dart' as http;

class MockClient extends Mock implements http.Client {}

void main() {
  test('products list returns data', () async {
    final mockClient = MockClient();
    
    when(mockClient.get(any, headers: anyNamed('headers')))
        .thenAnswer((_) async => http.Response('{"count": 10, "results": []}', 200));
    
    final client = Puxbay(
      apiKey: 'pb_test_key',
      httpClient: mockClient,
    );
    
    final products = await client.products.list();
    expect(products['count'], 10);
  });
}
```

## Flutter Integration

Works seamlessly with Flutter:

```dart
class ProductListScreen extends StatefulWidget {
  @override
  _ProductListScreenState createState() => _ProductListScreenState();
}

class _ProductListScreenState extends State<ProductListScreen> {
  late final Puxbay client;
  List<dynamic> products = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    client = Puxbay(apiKey: 'pb_your_key');
    loadProducts();
  }

  Future<void> loadProducts() async {
    try {
      final response = await client.products.list();
      setState(() {
        products = response['results'] as List<dynamic>;
        loading = false;
      });
    } catch (e) {
      setState(() => loading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }

  @override
  void dispose() {
    client.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (loading) return CircularProgressIndicator();
    return ListView.builder(
      itemCount: products.length,
      itemBuilder: (context, index) {
        final product = products[index];
        return ListTile(
          title: Text(product['name']),
          subtitle: Text('\$${product['price']}'),
        );
      },
    );
  }
}
```

## Requirements

- Dart SDK: >=2.17.0 <4.0.0
- Flutter: Compatible with all versions

## License

MIT License - see LICENSE file for details

## Support

- Documentation: https://docs.puxbay.com
- API Reference: https://api.puxbay.com/docs
- Issues: https://github.com/puxbay/puxbay-dart/issues
- Email: support@puxbay.com

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.
