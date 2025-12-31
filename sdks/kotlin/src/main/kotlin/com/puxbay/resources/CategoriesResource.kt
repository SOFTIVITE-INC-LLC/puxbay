package com.puxbay.resources

import com.puxbay.Puxbay
import com.puxbay.models.Category
import com.puxbay.models.PaginatedResponse
import io.ktor.http.HttpMethod

class CategoriesResource(client: Puxbay) : BaseResource(client) {
    suspend fun list(page: Int = 1): PaginatedResponse<Category> =
        client.request(HttpMethod.Get, "categories/?page=$page")
    
    suspend fun get(categoryId: String): Category =
        client.request(HttpMethod.Get, "categories/$categoryId/")
    
    suspend fun create(category: Category): Category =
        client.request(HttpMethod.Post, "categories/", category)
    
    suspend fun update(categoryId: String, category: Category): Category =
        client.request(HttpMethod.Patch, "categories/$categoryId/", category)
    
    suspend fun delete(categoryId: String) {
        client.request<Unit>(HttpMethod.Delete, "categories/$categoryId/")
    }
}
