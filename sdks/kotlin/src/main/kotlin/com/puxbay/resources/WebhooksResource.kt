package com.puxbay.resources

import com.puxbay.Puxbay
import com.puxbay.models.Webhook
import com.puxbay.models.PaginatedResponse
import io.ktor.http.HttpMethod

class WebhooksResource(client: Puxbay) : BaseResource(client) {
    suspend fun list(page: Int = 1): PaginatedResponse<Webhook> =
        client.request(HttpMethod.Get, "webhooks/?page=$page")
    
    suspend fun get(webhookId: String): Webhook =
        client.request(HttpMethod.Get, "webhooks/$webhookId/")
    
    suspend fun create(webhook: Webhook): Webhook =
        client.request(HttpMethod.Post, "webhooks/", webhook)
    
    suspend fun update(webhookId: String, webhook: Webhook): Webhook =
        client.request(HttpMethod.Patch, "webhooks/$webhookId/", webhook)
    
    suspend fun delete(webhookId: String) {
        client.request<Unit>(HttpMethod.Delete, "webhooks/$webhookId/")
    }
    
    suspend fun listEvents(webhookId: String, page: Int = 1): Map<String, Any> =
        client.request(HttpMethod.Get, "webhook-logs/?webhook=$webhookId&page=$page")
}
