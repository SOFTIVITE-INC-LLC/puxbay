import Foundation

public class CategoriesResource: BaseResource {
    public func list(page: Int = 1) async throws -> PaginatedResponse<Category> {
        try await client.request(method: "GET", endpoint: "categories/?page=\(page)")
    }
    
    public func get(categoryId: String) async throws -> Category {
        try await client.request(method: "GET", endpoint: "categories/\(categoryId)/")
    }
    
    public func create(category: Category) async throws -> Category {
        try await client.request(method: "POST", endpoint: "categories/", body: category)
    }
    
    public func update(categoryId: String, category: Category) async throws -> Category {
        try await client.request(method: "PATCH", endpoint: "categories/\(categoryId)/", body: category)
    }
    
    public func delete(categoryId: String) async throws {
        let _: EmptyResponse = try await client.request(method: "DELETE", endpoint: "categories/\(categoryId)/")
    }
}
