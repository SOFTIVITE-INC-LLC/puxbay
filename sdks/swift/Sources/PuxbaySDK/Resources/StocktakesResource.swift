import Foundation

public class StocktakesResource: BaseResource {
    public func list(page: Int = 1) async throws -> PaginatedResponse<Stocktake> {
        try await client.request(method: "GET", endpoint: "stocktakes/?page=\(page)")
    }
    
    public func get(stocktakeId: String) async throws -> Stocktake {
        try await client.request(method: "GET", endpoint: "stocktakes/\(stocktakeId)/")
    }
    
    public func create(stocktake: Stocktake) async throws -> Stocktake {
        try await client.request(method: "POST", endpoint: "stocktakes/", body: stocktake)
    }
    
    public func complete(stocktakeId: String) async throws -> Stocktake {
        try await client.request(method: "POST", endpoint: "stocktakes/\(stocktakeId)/complete/")
    }
}
