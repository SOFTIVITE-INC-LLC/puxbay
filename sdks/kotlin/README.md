# Puxbay Kotlin SDK

Official Kotlin SDK for the Puxbay POS API.

## Features

- ✅ Complete API coverage
- ✅ Coroutines support (suspend functions)
- ✅ Ktor-based networking
- ✅ Type-safe data classes
- ✅ Multiplatform ready structure

## Installation

Add to your `build.gradle.kts`:

```kotlin
dependencies {
    implementation("com.puxbay:puxbay-kotlin:1.0.0")
}
```

## Quick Start

```kotlin
import com.puxbay.Puxbay
import com.puxbay.models.PuxbayConfig
import kotlinx.coroutines.runBlocking

fun main() = runBlocking {
    val config = PuxbayConfig("pb_your_api_key")
    val client = Puxbay(config)

    // List products
    val products = client.products.list(page = 1)
    
    products.results.forEach { product ->
        println("${product.name}: $${product.price}")
    }
}
```

## Resources

Access resources fluently through the client:

```kotlin
// Products
client.products.list()
client.products.get("product-id")
client.products.create(newProduct)

// Orders
client.orders.list()
client.orders.create(newOrder)

// Customers
client.customers.list()
client.customers.get("customer-id")
```

## Error Handling

```kotlin
try {
    client.products.get("invalid")
} catch (e: PuxbayException) {
    println("API Error: ${e.message}")
}
```

## License

MIT License
