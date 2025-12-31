import Foundation

public class SuppliersResource: BaseResource {
    public func list(page: Int = 1, pageSize: Int = 20) async throws -> PaginatedResponse<Supplier> {
        try await client.request(method: "GET", endpoint: "suppliers/?page=\(page)&page_size=\(pageSize)")
    }
    
    public func get(supplierId: String) async throws -> Supplier {
        try await client.request(method: "GET", endpoint: "suppliers/\(supplierId)/")
    }
    
    public func create(supplier: Supplier) async throws -> Supplier {
        try await client.request(method: "POST", endpoint: "suppliers/", body: supplier)
    }
    
    public func update(supplierId: String, supplier: Supplier) async throws -> Supplier {
        try await client.request(method: "PATCH", endpoint: "suppliers/\(supplierId)/", body: supplier)
    }
    
    public func delete(supplierId: String) async throws {
        let _: EmptyResponse = try await client.request(method: "DELETE", endpoint: "suppliers/\(supplierId)/")
    }
}
