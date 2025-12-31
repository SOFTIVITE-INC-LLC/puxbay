package com.puxbay.resources

import com.puxbay.Puxbay
import com.puxbay.models.StockTransfer
import com.puxbay.models.PaginatedResponse
import io.ktor.http.HttpMethod

class StockTransfersResource(client: Puxbay) : BaseResource(client) {
    suspend fun list(page: Int = 1, status: String? = null): PaginatedResponse<StockTransfer> {
        val statusParam = if (status != null) "&status=$status" else ""
        return client.request(HttpMethod.Get, "stock-transfers/?page=$page$statusParam")
    }
    
    suspend fun get(transferId: String): StockTransfer =
        client.request(HttpMethod.Get, "stock-transfers/$transferId/")
    
    suspend fun create(transfer: StockTransfer): StockTransfer =
        client.request(HttpMethod.Post, "stock-transfers/", transfer)
    
    suspend fun complete(transferId: String): StockTransfer =
        client.request(HttpMethod.Post, "stock-transfers/$transferId/complete/")
}
