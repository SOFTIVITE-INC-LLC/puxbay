package com.puxbay.resources

import com.puxbay.Puxbay
import com.puxbay.models.ReturnRequest
import com.puxbay.models.PaginatedResponse
import io.ktor.http.HttpMethod

class ReturnsResource(client: Puxbay) : BaseResource(client) {
    suspend fun list(page: Int = 1): PaginatedResponse<ReturnRequest> =
        client.request(HttpMethod.Get, "returns/?page=$page")
    
    suspend fun get(returnId: String): ReturnRequest =
        client.request(HttpMethod.Get, "returns/$returnId/")
    
    suspend fun create(returnData: ReturnRequest): ReturnRequest =
        client.request(HttpMethod.Post, "returns/", returnData)
    
    suspend fun approve(returnId: String): ReturnRequest =
        client.request(HttpMethod.Post, "returns/$returnId/approve/")
}
