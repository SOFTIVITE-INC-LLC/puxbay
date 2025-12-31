import Foundation

public class StockTransfersResource: BaseResource {
    public func list(page: Int = 1, status: String? = nil) async throws -> PaginatedResponse<StockTransfer> {
        var query = "page=\(page)"
        if let status = status {
            query += "&status=\(status)"
        }
        return try await client.request(method: "GET", endpoint: "stock-transfers/?\(query)")
    }
    
    public func get(transferId: String) async throws -> StockTransfer {
        try await client.request(method: "GET", endpoint: "stock-transfers/\(transferId)/")
    }
    
    public func create(transfer: StockTransfer) async throws -> StockTransfer {
        try await client.request(method: "POST", endpoint: "stock-transfers/", body: transfer)
    }
    
    public func complete(transferId: String) async throws -> StockTransfer {
        try await client.request(method: "POST", endpoint: "stock-transfers/\(transferId)/complete/")
    }
}
