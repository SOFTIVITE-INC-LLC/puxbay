package com.puxbay.resources

import com.puxbay.Puxbay
import com.puxbay.models.GiftCard
import com.puxbay.models.PaginatedResponse
import io.ktor.http.HttpMethod

class GiftCardsResource(client: Puxbay) : BaseResource(client) {
    suspend fun list(page: Int = 1, status: String? = null): PaginatedResponse<GiftCard> {
        val statusParam = if (status != null) "&status=$status" else ""
        return client.request(HttpMethod.Get, "gift-cards/?page=$page$statusParam")
    }
    
    suspend fun get(cardId: String): GiftCard =
        client.request(HttpMethod.Get, "gift-cards/$cardId/")
    
    suspend fun create(card: GiftCard): GiftCard =
        client.request(HttpMethod.Post, "gift-cards/", card)
    
    suspend fun redeem(cardId: String, amount: Double): GiftCard =
        client.request(HttpMethod.Post, "gift-cards/$cardId/redeem/", mapOf("amount" to amount))
    
    suspend fun checkBalance(code: String): Map<String, Any> =
        client.request(HttpMethod.Get, "gift-cards/check-balance/?code=$code")
}
