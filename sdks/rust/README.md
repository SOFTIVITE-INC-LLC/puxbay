# Puxbay Rust SDK

Official Rust SDK for the Puxbay POS API.

## Features

- ✅ Complete API coverage (25+ endpoints)
- ✅ Async/await support with `tokio`
- ✅ Connection pooling with `reqwest`
- ✅ Automatic retry with exponential backoff
- ✅ Type-safe structs with `serde`
- ✅ Comprehensive error handling with `thiserror`

## Installation

Add this to your `Cargo.toml`:

```toml
[dependencies]
puxbay-sdk = "0.1.0"
tokio = { version = "1", features = ["full"] }
```

## Quick Start

```rust
use puxbay_sdk::{Puxbay, PuxbayConfig};
use std::error::Error;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Configure the client
    let config = PuxbayConfig::builder()
        .api_key("pb_your_api_key_here")
        .max_retries(5)
        .build();

    // Create client instance
    let client = Puxbay::new(config);

    // List products
    let products = client.products().list(1).await?;
    for product in products.results {
        println!("{}: ${}", product.name, product.price);
    }

    Ok(())
}
```

## Configuration Options

```rust
let config = PuxbayConfig::builder()
    .api_key("pb_your_api_key")
    .base_url("https://api.puxbay.com/api/v1") // Custom base URL
    .max_retries(3)                            // Max retry attempts
    .timeout(30)                               // Request timeout (seconds)
    .build();
```

## API Resources

### Products
```rust
// List products
let products = client.products().list(page).await?;

// Get product
let product = client.products().get("product-id").await?;

// Create product
let created = client.products().create(&new_product).await?;

// Update product
let updated = client.products().update("product-id", &updates).await?;

// Delete product
client.products().delete("product-id").await?;
```

### Orders
```rust
// List orders
let orders = client.orders().list(page, None).await?;

// Get order
let order = client.orders().get("order-id").await?;

// Create order
let created = client.orders().create(&new_order).await?;
```

### Customers
```rust
// List customers
let customers = client.customers().list(page, None).await?;

// Get customer
let customer = client.customers().get("customer-id").await?;
```

## Error Handling

The SDK uses `thiserror` to provide structured errors:

```rust
match client.products().get("invalid-id").await {
    Ok(product) => println!("Product: {:?}", product),
    Err(PuxbayError::NotFound(_)) => println!("Product not found"),
    Err(PuxbayError::AuthenticationError(_)) => println!("Invalid API key"),
    Err(e) => println!("Error: {}", e),
}
```

## License

MIT License
