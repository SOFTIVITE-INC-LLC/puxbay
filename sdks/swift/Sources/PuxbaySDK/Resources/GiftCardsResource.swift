import Foundation

public class GiftCardsResource: BaseResource {
    public func list(page: Int = 1, status: String? = nil) async throws -> PaginatedResponse<GiftCard> {
        var query = "page=\(page)"
        if let status = status {
            query += "&status=\(status)"
        }
        return try await client.request(method: "GET", endpoint: "gift-cards/?\(query)")
    }
    
    public func get(cardId: String) async throws -> GiftCard {
        try await client.request(method: "GET", endpoint: "gift-cards/\(cardId)/")
    }
    
    public func create(card: GiftCard) async throws -> GiftCard {
        try await client.request(method: "POST", endpoint: "gift-cards/", body: card)
    }
    
    public func redeem(cardId: String, amount: Double) async throws -> GiftCard {
        struct RedeemBody: Codable { let amount: Double }
        return try await client.request(method: "POST", endpoint: "gift-cards/\(cardId)/redeem/", body: RedeemBody(amount: amount))
    }
    
    public func checkBalance(code: String) async throws -> [String: Double] { // Assuming response is simple JSON like {"balance": 50.0}
        // Swift Codable strictness requires we know the response type.
        // Assuming API returns {"balance": 100.0} or similar.
        // If dynamic, [String: Double] works if values are doubles.
        try await client.request(method: "GET", endpoint: "gift-cards/check-balance/?code=\(code)")
    }
}
