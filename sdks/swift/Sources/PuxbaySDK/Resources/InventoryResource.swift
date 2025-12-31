import Foundation

public class InventoryResource: BaseResource {
    public func getStockLevels(branchId: String) async throws -> [StockLevel] {
        struct Response: Codable {
            let results: [StockLevel]
        }
        // Assuming array response
        return try await client.request(method: "GET", endpoint: "inventory/stock-levels/?branch=\(branchId)")
    }
    
    public func getProductStock(productId: String, branchId: String) async throws -> StockLevel {
        try await client.request(method: "GET", endpoint: "inventory/product-stock/?product=\(productId)&branch=\(branchId)")
    }
}

public struct StockLevel: Codable {
    public let productId: String
    public let branchId: String
    public let quantity: Int
}
