# Puxbay Swift SDK

Official Swift SDK for the Puxbay POS API.

## Features

- ✅ Complete API coverage
- ✅ Native async/await support
- ✅ Codable structs
- ✅ URLSession based
- ✅ macOS/iOS/tvOS/watchOS compatible

## Installation

### Swift Package Manager

Add this to your `Package.swift`:

```swift
dependencies: [
    .package(url: "https://github.com/puxbay/puxbay-swift.git", from: "1.0.0")
]
```

## Quick Start

```swift
import PuxbaySDK

// Configure
let config = PuxbayConfig(apiKey: "pb_your_api_key")
let client = Puxbay(config: config)

// Use async/await
do {
    let products = try await client.products.list(page: 1)
    
    for product in products.results {
        print("\(product.name): $\(product.price)")
    }
} catch {
    print("Error: \(error)")
}
```

## Resources

```swift
// Products
try await client.products.list()
try await client.products.get("product-id")

// Orders
try await client.orders.list()

// Customers
try await client.customers.list()
```

## License

MIT License
