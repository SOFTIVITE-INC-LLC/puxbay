package com.puxbay.examples

import com.puxbay.Puxbay
import com.puxbay.models.PuxbayConfig
import kotlinx.coroutines.runBlocking

fun main() = runBlocking {
    val apiKey = System.getenv("PUXBAY_API_KEY")
    if (apiKey == null) {
        println("PUXBAY_API_KEY must be set")
        return@runBlocking
    }

    val config = PuxbayConfig(apiKey)
    val client = Puxbay(config)

    println("Fetching products...")
    try {
        val products = client.products.list(page = 1)
        products.results.forEach { product ->
            println("- ${product.name} ($${product.price})")
        }
    } catch (e: Exception) {
        println("Error: ${e.message}")
    }
}
