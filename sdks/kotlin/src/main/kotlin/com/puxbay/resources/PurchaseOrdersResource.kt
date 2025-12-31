package com.puxbay.resources

import com.puxbay.Puxbay
import com.puxbay.models.PurchaseOrder
import com.puxbay.models.PaginatedResponse
import io.ktor.http.HttpMethod

class PurchaseOrdersResource(client: Puxbay) : BaseResource(client) {
    suspend fun list(page: Int = 1, status: String? = null): PaginatedResponse<PurchaseOrder> {
        val statusParam = if (status != null) "&status=$status" else ""
        return client.request(HttpMethod.Get, "purchase-orders/?page=$page$statusParam")
    }
    
    suspend fun get(poId: String): PurchaseOrder =
        client.request(HttpMethod.Get, "purchase-orders/$poId/")
    
    suspend fun create(po: PurchaseOrder): PurchaseOrder =
        client.request(HttpMethod.Post, "purchase-orders/", po)
    
    suspend fun update(poId: String, po: PurchaseOrder): PurchaseOrder =
        client.request(HttpMethod.Patch, "purchase-orders/$poId/", po)
        
    suspend fun receive(poId: String, items: List<Map<String, Any>>): PurchaseOrder =
        client.request(HttpMethod.Post, "purchase-orders/$poId/receive/", mapOf("items" to items))
}
