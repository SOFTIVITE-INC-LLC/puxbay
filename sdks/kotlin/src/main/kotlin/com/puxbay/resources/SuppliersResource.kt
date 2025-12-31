package com.puxbay.resources

import com.puxbay.Puxbay
import com.puxbay.models.Supplier
import com.puxbay.models.PaginatedResponse
import io.ktor.http.HttpMethod

class SuppliersResource(client: Puxbay) : BaseResource(client) {
    suspend fun list(page: Int = 1, pageSize: Int = 20): PaginatedResponse<Supplier> =
        client.request(HttpMethod.Get, "suppliers/?page=$page&page_size=$pageSize")
    
    suspend fun get(supplierId: String): Supplier =
        client.request(HttpMethod.Get, "suppliers/$supplierId/")
    
    suspend fun create(supplier: Supplier): Supplier =
        client.request(HttpMethod.Post, "suppliers/", supplier)
    
    suspend fun update(supplierId: String, supplier: Supplier): Supplier =
        client.request(HttpMethod.Patch, "suppliers/$supplierId/", supplier)
    
    suspend fun delete(supplierId: String) {
        client.request<Unit>(HttpMethod.Delete, "suppliers/$supplierId/")
    }
}
