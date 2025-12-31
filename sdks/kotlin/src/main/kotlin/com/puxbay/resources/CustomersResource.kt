package com.puxbay.resources

import com.puxbay.Puxbay
import com.puxbay.models.Customer
import com.puxbay.models.PaginatedResponse
import io.ktor.http.HttpMethod

class CustomersResource(client: Puxbay) : BaseResource(client) {
    suspend fun list(page: Int = 1, pageSize: Int = 20): PaginatedResponse<Customer> =
        client.request(HttpMethod.Get, "customers/?page=$page&page_size=$pageSize")
    
    suspend fun get(customerId: String): Customer =
        client.request(HttpMethod.Get, "customers/$customerId/")
    
    suspend fun create(customer: Customer): Customer =
        client.request(HttpMethod.Post, "customers/", customer)
    
    suspend fun update(customerId: String, customer: Customer): Customer =
        client.request(HttpMethod.Patch, "customers/$customerId/", customer)
        
    suspend fun delete(customerId: String) {
        client.request<Unit>(HttpMethod.Delete, "customers/$customerId/")
    }
        
    suspend fun adjustLoyaltyPoints(customerId: String, points: Int, description: String): Customer =
        client.request(HttpMethod.Post, "customers/$customerId/adjust-loyalty-points/", 
            mapOf("points" to points, "description" to description))
}
