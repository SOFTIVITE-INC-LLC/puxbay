import Foundation

public class ProductsResource: BaseResource {
    public func list(page: Int = 1, pageSize: Int = 20) async throws -> PaginatedResponse<Product> {
        try await client.request(method: "GET", endpoint: "products/?page=\(page)&page_size=\(pageSize)")
    }
    
    public func get(productId: String) async throws -> Product {
        try await client.request(method: "GET", endpoint: "products/\(productId)/")
    }
    
    public func create(product: Product) async throws -> Product {
        try await client.request(method: "POST", endpoint: "products/", body: product)
    }
    
    public func update(productId: String, product: Product) async throws -> Product {
        try await client.request(method: "PATCH", endpoint: "products/\(productId)/", body: product)
    }
    
    public func delete(productId: String) async throws {
        let _: EmptyResponse = try await client.request(method: "DELETE", endpoint: "products/\(productId)/")
    }
    
    public func adjustStock(productId: String, quantity: Int, reason: String) async throws -> Product {
        let body = ["quantity": quantity, "reason": reason] as [String: Any]
        // Note: Using Any here might need custom encoding helper in Helper utils or manual dict
        // Swift Codable doesn't support [String: Any] directly.
        // I will create a simple struct for this body or use a dictionary wrapper helper if needed.
        // For simple cases, creating a quick struct is safer.
        struct AdjustmentBody: Codable {
            let quantity: Int
            let reason: String
        }
        return try await client.request(method: "POST", endpoint: "products/\(productId)/stock-adjustment/", body: AdjustmentBody(quantity: quantity, reason: reason))
    }
}
