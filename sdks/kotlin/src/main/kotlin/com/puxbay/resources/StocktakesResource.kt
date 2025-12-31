package com.puxbay.resources

import com.puxbay.Puxbay
import com.puxbay.models.Stocktake
import com.puxbay.models.PaginatedResponse
import io.ktor.http.HttpMethod

class StocktakesResource(client: Puxbay) : BaseResource(client) {
    suspend fun list(page: Int = 1): PaginatedResponse<Stocktake> =
        client.request(HttpMethod.Get, "stocktakes/?page=$page")
    
    suspend fun get(stocktakeId: String): Stocktake =
        client.request(HttpMethod.Get, "stocktakes/$stocktakeId/")
    
    suspend fun create(stocktake: Stocktake): Stocktake =
        client.request(HttpMethod.Post, "stocktakes/", stocktake)
    
    suspend fun complete(stocktakeId: String): Stocktake =
        client.request(HttpMethod.Post, "stocktakes/$stocktakeId/complete/")
}
