# Puxbay Java SDK

Official Java SDK for the Puxbay POS API.

## Features

- ✅ Complete API coverage (25+ endpoints)
- ✅ Connection pooling with OkHttp
- ✅ Automatic retry with exponential backoff
- ✅ Comprehensive error handling
- ✅ Type-safe models
- ✅ Builder pattern for configuration
- ✅ Java 8+ compatible

## Installation

### Maven

```xml
<dependency>
    <groupId>com.puxbay</groupId>
    <artifactId>puxbay-java</artifactId>
    <version>1.0.0</version>
</dependency>
```

### Gradle

```gradle
implementation 'com.puxbay:puxbay-java:1.0.0'
```

## Quick Start

```java
import com.puxbay.*;
import com.puxbay.models.*;

// Configure the client
PuxbayConfig config = new PuxbayConfig.Builder("pb_your_api_key_here")
    .maxRetries(5)
    .timeout(30)
    .build();

// Create client instance
Puxbay client = new Puxbay(config);

// List products
PaginatedResponse<Product> products = client.products().list(1, 20);
for (Product product : products.getResults()) {
    System.out.println(product.getName() + ": $" + product.getPrice());
}

// Create a new product
Product newProduct = new Product();
newProduct.setName("New Product");
newProduct.setSku("SKU-001");
newProduct.setPrice(29.99);
newProduct.setStockQuantity(100);
newProduct.setCategory("category-id");

Product created = client.products().create(newProduct);

// Close client when done
client.close();
```

## Configuration Options

```java
PuxbayConfig config = new PuxbayConfig.Builder("pb_your_api_key")
    .baseUrl("https://api.puxbay.com/api/v1")  // Custom base URL
    .timeout(30)                                 // Request timeout (seconds)
    .maxRetries(3)                              // Max retry attempts
    .maxIdleConnections(10)                     // Connection pool size
    .keepAliveDuration(300)                     // Keep-alive duration (seconds)
    .build();
```

## API Resources

### Products
```java
// List products
PaginatedResponse<Product> products = client.products().list(page, pageSize);

// Get product
Product product = client.products().get("product-id");

// Create product
Product created = client.products().create(newProduct);

// Update product
Product updated = client.products().update("product-id", product);

// Delete product
client.products().delete("product-id");

// Adjust stock
client.products().adjustStock("product-id", 10, "Added inventory");
```

### Orders
```java
// List orders
PaginatedResponse<Order> orders = client.orders().list(page, pageSize);

// Get order
Order order = client.orders().get("order-id");

// Create order
Order created = client.orders().create(newOrder);

// Cancel order
Order cancelled = client.orders().cancel("order-id");
```

### Customers
```java
// List customers
PaginatedResponse<Customer> customers = client.customers().list(page, pageSize);

// Get customer
Customer customer = client.customers().get("customer-id");

// Create customer
Customer created = client.customers().create(newCustomer);

// Update customer
Customer updated = client.customers().update("customer-id", customer);

// Adjust loyalty points
Customer adjusted = client.customers().adjustLoyaltyPoints("customer-id", 100, "Bonus points");
```

### All Resources

- `client.products()` - Product management
- `client.orders()` - Order management
- `client.customers()` - Customer management
- `client.inventory()` - Inventory tracking
- `client.reports()` - Sales reports & analytics
- `client.categories()` - Product categories
- `client.suppliers()` - Supplier management
- `client.purchaseOrders()` - Purchase orders
- `client.stockTransfers()` - Stock transfers
- `client.stocktakes()` - Stocktake sessions
- `client.cashDrawers()` - Cash drawer management
- `client.giftCards()` - Gift card operations
- `client.expenses()` - Expense tracking
- `client.branches()` - Branch management
- `client.staff()` - Staff management
- `client.webhooks()` - Webhook configuration
- `client.notifications()` - Notifications
- `client.returns()` - Return processing

## Error Handling

```java
import com.puxbay.exceptions.*;

try {
    Product product = client.products().get("invalid-id");
} catch (NotFoundException e) {
    System.err.println("Product not found: " + e.getMessage());
} catch (AuthenticationException e) {
    System.err.println("Invalid API key: " + e.getMessage());
} catch (RateLimitException e) {
    System.err.println("Rate limit exceeded: " + e.getMessage());
} catch (ValidationException e) {
    System.err.println("Validation error: " + e.getMessage());
} catch (ServerException e) {
    System.err.println("Server error: " + e.getMessage());
} catch (PuxbayException e) {
    System.err.println("API error: " + e.getMessage());
    System.err.println("Status code: " + e.getStatusCode());
}
```

## Building from Source

```bash
git clone https://github.com/puxbay/puxbay-java.git
cd puxbay-java
mvn clean install
```

## Requirements

- Java 8 or higher
- Maven 3.6+ or Gradle 6.0+

## Dependencies

- OkHttp 4.12.0 - HTTP client
- Gson 2.10.1 - JSON serialization
- SLF4J 2.0.9 - Logging API

## License

MIT License - see LICENSE file for details

## Support

- Documentation: https://docs.puxbay.com
- API Reference: https://api.puxbay.com/docs
- Issues: https://github.com/puxbay/puxbay-java/issues
- Email: support@puxbay.com
