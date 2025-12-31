import Foundation

public class CustomersResource: BaseResource {
    public func list(page: Int = 1, pageSize: Int = 20) async throws -> PaginatedResponse<Customer> {
        try await client.request(method: "GET", endpoint: "customers/?page=\(page)&page_size=\(pageSize)")
    }
    
    public func get(customerId: String) async throws -> Customer {
        try await client.request(method: "GET", endpoint: "customers/\(customerId)/")
    }
    
    public func create(customer: Customer) async throws -> Customer {
        try await client.request(method: "POST", endpoint: "customers/", body: customer)
    }
    
    public func update(customerId: String, customer: Customer) async throws -> Customer {
        try await client.request(method: "PATCH", endpoint: "customers/\(customerId)/", body: customer)
    }
    
    public func delete(customerId: String) async throws {
        let _: EmptyResponse = try await client.request(method: "DELETE", endpoint: "customers/\(customerId)/")
    }
    
    public func adjustLoyaltyPoints(customerId: String, points: Int, description: String) async throws -> Customer {
        struct AdjustmentBody: Codable {
            let points: Int
            let description: String
        }
        return try await client.request(method: "POST", endpoint: "customers/\(customerId)/adjust-loyalty-points/", body: AdjustmentBody(points: points, description: description))
    }
}
