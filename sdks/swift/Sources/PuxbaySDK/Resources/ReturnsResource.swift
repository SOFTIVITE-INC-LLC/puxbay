import Foundation

public class ReturnsResource: BaseResource {
    public func list(page: Int = 1) async throws -> PaginatedResponse<ReturnRequest> {
        try await client.request(method: "GET", endpoint: "returns/?page=\(page)")
    }
    
    public func get(returnId: String) async throws -> ReturnRequest {
        try await client.request(method: "GET", endpoint: "returns/\(returnId)/")
    }
    
    public func create(returnData: ReturnRequest) async throws -> ReturnRequest {
        try await client.request(method: "POST", endpoint: "returns/", body: returnData)
    }
    
    public func approve(returnId: String) async throws -> ReturnRequest {
        try await client.request(method: "POST", endpoint: "returns/\(returnId)/approve/")
    }
}
