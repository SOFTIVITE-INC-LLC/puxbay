package com.puxbay.resources

import com.puxbay.Puxbay
import com.puxbay.models.Order
import com.puxbay.models.PaginatedResponse
import io.ktor.http.HttpMethod

class OrdersResource(client: Puxbay) : BaseResource(client) {
    suspend fun list(page: Int = 1, pageSize: Int = 20): PaginatedResponse<Order> =
        client.request(HttpMethod.Get, "orders/?page=$page&page_size=$pageSize")
    
    suspend fun get(orderId: String): Order =
        client.request(HttpMethod.Get, "orders/$orderId/")
    
    suspend fun create(order: Order): Order =
        client.request(HttpMethod.Post, "orders/", order)
        
    suspend fun cancel(orderId: String): Order =
        client.request(HttpMethod.Post, "orders/$orderId/cancel/")
}
