package com.puxbay.resources

import com.puxbay.Puxbay
import com.puxbay.models.Staff
import com.puxbay.models.PaginatedResponse
import io.ktor.http.HttpMethod

class StaffResource(client: Puxbay) : BaseResource(client) {
    suspend fun list(page: Int = 1, role: String? = null): PaginatedResponse<Staff> {
        val roleParam = if (role != null) "&role=$role" else ""
        return client.request(HttpMethod.Get, "staff/?page=$page$roleParam")
    }
    
    suspend fun get(staffId: String): Staff =
        client.request(HttpMethod.Get, "staff/$staffId/")
    
    suspend fun create(staff: Staff): Staff =
        client.request(HttpMethod.Post, "staff/", staff)
    
    suspend fun update(staffId: String, staff: Staff): Staff =
        client.request(HttpMethod.Patch, "staff/$staffId/", staff)
    
    suspend fun delete(staffId: String) {
        client.request<Unit>(HttpMethod.Delete, "staff/$staffId/")
    }
}
