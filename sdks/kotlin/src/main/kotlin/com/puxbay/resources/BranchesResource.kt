package com.puxbay.resources

import com.puxbay.Puxbay
import com.puxbay.models.Branch
import com.puxbay.models.PaginatedResponse
import io.ktor.http.HttpMethod

class BranchesResource(client: Puxbay) : BaseResource(client) {
    suspend fun list(page: Int = 1): PaginatedResponse<Branch> =
        client.request(HttpMethod.Get, "branches/?page=$page")
    
    suspend fun get(branchId: String): Branch =
        client.request(HttpMethod.Get, "branches/$branchId/")
    
    suspend fun create(branch: Branch): Branch =
        client.request(HttpMethod.Post, "branches/", branch)
    
    suspend fun update(branchId: String, branch: Branch): Branch =
        client.request(HttpMethod.Patch, "branches/$branchId/", branch)
    
    suspend fun delete(branchId: String) {
        client.request<Unit>(HttpMethod.Delete, "branches/$branchId/")
    }
}
