# Puxbay .NET SDK

Official .NET SDK for the Puxbay POS API.

## Features

- ✅ Complete API coverage (25+ endpoints)
- ✅ Async/await throughout
- ✅ Connection pooling with HttpClient
- ✅ Automatic retry with Polly
- ✅ Strong typing with C# models
- ✅ XML documentation for IntelliSense
- ✅ .NET Standard 2.0+ (compatible with .NET Core, .NET 5+, .NET Framework)

## Installation

### Package Manager Console
```powershell
Install-Package Puxbay.SDK
```

### .NET CLI
```bash
dotnet add package Puxbay.SDK
```

### PackageReference
```xml
<PackageReference Include="Puxbay.SDK" Version="1.0.0" />
```

## Quick Start

```csharp
using Puxbay.SDK;
using Puxbay.SDK.Models;

// Configure the client
var config = new PuxbayConfig
{
    ApiKey = "pb_your_api_key_here",
    MaxRetries = 5,
    Timeout = TimeSpan.FromSeconds(30)
};

// Create client instance
using var client = new PuxbayClient(config);

// List products
var products = await client.Products.ListAsync(1, 20);
foreach (var product in products.Results)
{
    Console.WriteLine($"{product.Name}: ${product.Price}");
}

// Create a new product
var newProduct = new Product
{
    Name = "New Product",
    Sku = "SKU-001",
    Price = 29.99m,
    StockQuantity = 100,
    Category = "category-id"
};

var created = await client.Products.CreateAsync(newProduct);
```

## Configuration Options

```csharp
var config = new PuxbayConfig
{
    ApiKey = "pb_your_api_key",
    BaseUrl = "https://api.puxbay.com/api/v1",  // Custom base URL
    Timeout = TimeSpan.FromSeconds(30),          // Request timeout
    MaxRetries = 3,                              // Max retry attempts
    MaxConnectionsPerServer = 10                 // Connection pool size
};
```

## API Resources

### Products
```csharp
// List products
var products = await client.Products.ListAsync(page, pageSize);

// Get product
var product = await client.Products.GetAsync("product-id");

// Create product
var created = await client.Products.CreateAsync(newProduct);

// Update product
var updated = await client.Products.UpdateAsync("product-id", product);

// Delete product
await client.Products.DeleteAsync("product-id");

// Adjust stock
await client.Products.AdjustStockAsync("product-id", 10, "Added inventory");
```

### Orders
```csharp
// List orders
var orders = await client.Orders.ListAsync(page, pageSize);

// Get order
var order = await client.Orders.GetAsync("order-id");

// Create order
var created = await client.Orders.CreateAsync(newOrder);

// Cancel order
var cancelled = await client.Orders.CancelAsync("order-id");
```

### Customers
```csharp
// List customers
var customers = await client.Customers.ListAsync(page, pageSize);

// Get customer
var customer = await client.Customers.GetAsync("customer-id");

// Create customer
var created = await client.Customers.CreateAsync(newCustomer);

// Update customer
var updated = await client.Customers.UpdateAsync("customer-id", customer);

// Adjust loyalty points
var adjusted = await client.Customers.AdjustLoyaltyPointsAsync("customer-id", 100, "Bonus points");
```

### All Resources

- `client.Products` - Product management
- `client.Orders` - Order management
- `client.Customers` - Customer management
- `client.Inventory` - Inventory tracking
- `client.Reports` - Sales reports & analytics
- `client.Categories` - Product categories
- `client.Suppliers` - Supplier management
- `client.PurchaseOrders` - Purchase orders
- `client.StockTransfers` - Stock transfers
- `client.Stocktakes` - Stocktake sessions
- `client.CashDrawers` - Cash drawer management
- `client.GiftCards` - Gift card operations
- `client.Expenses` - Expense tracking
- `client.Branches` - Branch management
- `client.Staff` - Staff management
- `client.Webhooks` - Webhook configuration
- `client.Notifications` - Notifications
- `client.Returns` - Return processing

## Error Handling

```csharp
using Puxbay.SDK.Exceptions;

try
{
    var product = await client.Products.GetAsync("invalid-id");
}
catch (NotFoundException ex)
{
    Console.WriteLine($"Product not found: {ex.Message}");
}
catch (AuthenticationException ex)
{
    Console.WriteLine($"Invalid API key: {ex.Message}");
}
catch (RateLimitException ex)
{
    Console.WriteLine($"Rate limit exceeded: {ex.Message}");
}
catch (ValidationException ex)
{
    Console.WriteLine($"Validation error: {ex.Message}");
}
catch (ServerException ex)
{
    Console.WriteLine($"Server error: {ex.Message}");
}
catch (PuxbayException ex)
{
    Console.WriteLine($"API error: {ex.Message}");
    Console.WriteLine($"Status code: {ex.StatusCode}");
}
```

## Building from Source

```bash
git clone https://github.com/puxbay/puxbay-dotnet.git
cd puxbay-dotnet
dotnet build
dotnet test
```

## Requirements

- .NET Standard 2.0+
- .NET Core 2.0+, .NET 5+, or .NET Framework 4.6.1+

## Dependencies

- Newtonsoft.Json 13.0.3 - JSON serialization
- Polly 8.2.0 - Retry policies
- System.Net.Http 4.3.4 - HTTP client

## License

MIT License - see LICENSE file for details

## Support

- Documentation: https://docs.puxbay.com
- API Reference: https://api.puxbay.com/docs
- Issues: https://github.com/puxbay/puxbay-dotnet/issues
- Email: support@puxbay.com
