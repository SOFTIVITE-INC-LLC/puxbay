# Puxbay Go SDK

Official Go client library for the Puxbay POS API.

## Installation

```bash
go get github.com/puxbay/puxbay-go
```

## Quick Start

```go
package main

import (
    "fmt"
    "log"
    
    "github.com/puxbay/puxbay-go"
)

func main() {
    // Initialize the client
    client := puxbay.NewClient("pb_your_api_key_here")
    
    // List products
    products, err := client.Products.List(&puxbay.ListParams{
        Page:     1,
        PageSize: 20,
    })
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Found %d products\n", products.Count)
    
    // Create a customer
    customer, err := client.Customers.Create(&puxbay.Customer{
        Name:  "John Doe",
        Email: "john@example.com",
        Phone: "+1234567890",
    })
    if err != nil {
        log.Fatal(err)
    }
    
    // Create an order
    order, err := client.Orders.Create(&puxbay.Order{
        Customer: customer.ID,
        Items: []puxbay.OrderItem{
            {Product: "product-uuid", Quantity: 2, Price: 29.99},
        },
        PaymentMethod: "cash",
        Status:        "completed",
    })
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("Order created: %s\n", order.ID)
}
```

## Authentication

Get your API key from the Developer Settings in your Puxbay dashboard.

## Available Resources

### Products

```go
// List products
products, err := client.Products.List(&puxbay.ListParams{
    Search: "laptop",
})

// Get a product
product, err := client.Products.Get("product-uuid")

// Create a product
product, err := client.Products.Create(&puxbay.Product{
    Name:     "Laptop",
    SKU:      "LAP-001",
    Price:    999.99,
    Category: "category-uuid",
})

// Update a product
product, err := client.Products.Update("product-uuid", &puxbay.Product{
    Price: 899.99,
})

// Adjust stock
product, err := client.Products.AdjustStock("product-uuid", 10, "restock")
```

### Orders

```go
// List orders
orders, err := client.Orders.List(&puxbay.OrderListParams{
    Status: "completed",
})

// Get an order
order, err := client.Orders.Get("order-uuid")

// Cancel an order
order, err := client.Orders.Cancel("order-uuid", "Customer request")
```

### Customers

```go
// List customers
customers, err := client.Customers.List(&puxbay.ListParams{
    Search: "john",
})

// Add loyalty points
customer, err := client.Customers.AddLoyaltyPoints("customer-uuid", 100, "Purchase reward")

// Add store credit
customer, err := client.Customers.AddStoreCredit("customer-uuid", 50.00, "Refund")
```

### Inventory

```go
// Get stock levels
stock, err := client.Inventory.GetStockLevels("")

// Get low stock items
lowStock, err := client.Inventory.GetLowStock(10)

// Create stock transfer
transfer, err := client.Inventory.CreateTransfer(&puxbay.StockTransfer{
    FromBranch: "branch-uuid-1",
    ToBranch:   "branch-uuid-2",
    Items: []puxbay.StockTransferItem{
        {Product: "product-uuid", Quantity: 10},
    },
})
```

### Reports

```go
// Sales summary
sales, err := client.Reports.SalesSummary("2024-01-01", "2024-12-31", "")

// Product performance
performance, err := client.Reports.ProductPerformance("2024-01-01", "2024-12-31", 10)

// Customer analytics
analytics, err := client.Reports.CustomerAnalytics("2024-01-01", "2024-12-31")

// Profit & loss
pl, err := client.Reports.ProfitLoss("2024-01-01", "2024-12-31", "")
```

## Error Handling

```go
import "github.com/puxbay/puxbay-go"

product, err := client.Products.Get("invalid-uuid")
if err != nil {
    switch e := err.(type) {
    case *puxbay.AuthenticationError:
        fmt.Println("Invalid API key")
    case *puxbay.RateLimitError:
        fmt.Println("Rate limit exceeded")
    case *puxbay.ValidationError:
        fmt.Printf("Validation error: %s\n", e.Message)
    case *puxbay.NotFoundError:
        fmt.Println("Resource not found")
    default:
        fmt.Printf("Error: %s\n", err)
    }
}
```

## Configuration

```go
import "time"

// Custom configuration
client := puxbay.NewClientWithConfig(
    "pb_your_key",
    "https://your-domain.com/api/v1",
    60 * time.Second,
)
```

## Support

- Documentation: https://docs.puxbay.com
- API Reference: https://api.puxbay.com/docs
- Issues: https://github.com/puxbay/puxbay-go/issues

## License

MIT License
