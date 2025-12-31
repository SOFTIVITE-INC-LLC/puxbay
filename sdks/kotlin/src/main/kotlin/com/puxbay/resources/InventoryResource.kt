package com.puxbay.resources

import com.puxbay.Puxbay
import io.ktor.http.HttpMethod

class InventoryResource(client: Puxbay) : BaseResource(client) {
    suspend fun getStockLevels(branchId: String): List<Map<String, Any>> =
        client.request(HttpMethod.Get, "inventory/stock-levels/?branch=$branchId")
    
    suspend fun getProductStock(productId: String, branchId: String): Map<String, Any> =
        client.request(HttpMethod.Get, "inventory/product-stock/?product=$productId&branch=$branchId")
}
