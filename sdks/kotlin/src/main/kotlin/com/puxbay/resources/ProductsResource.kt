package com.puxbay.resources

import com.puxbay.Puxbay
import com.puxbay.models.Product
import com.puxbay.models.PaginatedResponse
import io.ktor.http.HttpMethod

class ProductsResource(client: Puxbay) : BaseResource(client) {
    suspend fun list(page: Int = 1, pageSize: Int = 20): PaginatedResponse<Product> =
        client.request(HttpMethod.Get, "products/?page=$page&page_size=$pageSize")
    
    suspend fun get(productId: String): Product =
        client.request(HttpMethod.Get, "products/$productId/")
    
    suspend fun create(product: Product): Product =
        client.request(HttpMethod.Post, "products/", product)
    
    suspend fun update(productId: String, product: Product): Product =
        client.request(HttpMethod.Patch, "products/$productId/", product)
    
    suspend fun delete(productId: String) {
        client.request<Unit>(HttpMethod.Delete, "products/$productId/")
    }
    
    suspend fun adjustStock(productId: String, quantity: Int, reason: String): Product =
        client.request(HttpMethod.Post, "products/$productId/stock-adjustment/", 
            mapOf("quantity" to quantity, "reason" to reason))
}
