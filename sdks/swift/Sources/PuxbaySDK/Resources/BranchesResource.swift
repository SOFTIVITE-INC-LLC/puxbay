import Foundation

public class BranchesResource: BaseResource {
    public func list(page: Int = 1) async throws -> PaginatedResponse<Branch> {
        try await client.request(method: "GET", endpoint: "branches/?page=\(page)")
    }
    
    public func get(branchId: String) async throws -> Branch {
        try await client.request(method: "GET", endpoint: "branches/\(branchId)/")
    }
    
    public func create(branch: Branch) async throws -> Branch {
        try await client.request(method: "POST", endpoint: "branches/", body: branch)
    }
    
    public func update(branchId: String, branch: Branch) async throws -> Branch {
        try await client.request(method: "PATCH", endpoint: "branches/\(branchId)/", body: branch)
    }
    
    public func delete(branchId: String) async throws {
        let _: EmptyResponse = try await client.request(method: "DELETE", endpoint: "branches/\(branchId)/")
    }
}
