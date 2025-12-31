import Foundation

public class OrdersResource: BaseResource {
    public func list(page: Int = 1, pageSize: Int = 20) async throws -> PaginatedResponse<Order> {
        try await client.request(method: "GET", endpoint: "orders/?page=\(page)&page_size=\(pageSize)")
    }
    
    public func get(orderId: String) async throws -> Order {
        try await client.request(method: "GET", endpoint: "orders/\(orderId)/")
    }
    
    public func create(order: Order) async throws -> Order {
        try await client.request(method: "POST", endpoint: "orders/", body: order)
    }
    
    public func cancel(orderId: String) async throws -> Order {
        let _: EmptyResponse = try await client.request(method: "POST", endpoint: "orders/\(orderId)/cancel/")
        return try await get(orderId: orderId) // Re-fetch or simplistic implementation
    }
}
