package com.puxbay.resources

import com.puxbay.Puxbay
import com.puxbay.models.Notification
import com.puxbay.models.PaginatedResponse
import io.ktor.http.HttpMethod

class NotificationsResource(client: Puxbay) : BaseResource(client) {
    suspend fun list(page: Int = 1): PaginatedResponse<Notification> =
        client.request(HttpMethod.Get, "notifications/?page=$page")
    
    suspend fun get(notificationId: String): Notification =
        client.request(HttpMethod.Get, "notifications/$notificationId/")
    
    suspend fun markAsRead(notificationId: String): Notification =
        client.request(HttpMethod.Post, "notifications/$notificationId/mark-read/")
}
