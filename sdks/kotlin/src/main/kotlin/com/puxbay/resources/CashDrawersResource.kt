package com.puxbay.resources

import com.puxbay.Puxbay
import com.puxbay.models.CashDrawerSession
import com.puxbay.models.PaginatedResponse
import io.ktor.http.HttpMethod

class CashDrawersResource(client: Puxbay) : BaseResource(client) {
    suspend fun list(page: Int = 1): PaginatedResponse<CashDrawerSession> =
        client.request(HttpMethod.Get, "cash-drawers/?page=$page")
    
    suspend fun get(drawerId: String): CashDrawerSession =
        client.request(HttpMethod.Get, "cash-drawers/$drawerId/")
    
    suspend fun open(drawerData: Map<String, Any>): CashDrawerSession =
        client.request(HttpMethod.Post, "cash-drawers/", drawerData)
    
    suspend fun close(drawerId: String, actualCash: Double): CashDrawerSession =
        client.request(HttpMethod.Post, "cash-drawers/$drawerId/close/", mapOf("actual_cash" to actualCash))
}
