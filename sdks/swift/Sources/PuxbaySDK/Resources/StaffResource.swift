import Foundation

public class StaffResource: BaseResource {
    public func list(page: Int = 1, role: String? = nil) async throws -> PaginatedResponse<Staff> {
        var query = "page=\(page)"
        if let role = role {
            query += "&role=\(role)"
        }
        return try await client.request(method: "GET", endpoint: "staff/?\(query)")
    }
    
    public func get(staffId: String) async throws -> Staff {
        try await client.request(method: "GET", endpoint: "staff/\(staffId)/")
    }
    
    public func create(staff: Staff) async throws -> Staff {
        try await client.request(method: "POST", endpoint: "staff/", body: staff)
    }
    
    public func update(staffId: String, staff: Staff) async throws -> Staff {
        try await client.request(method: "PATCH", endpoint: "staff/\(staffId)/", body: staff)
    }
    
    public func delete(staffId: String) async throws {
        let _: EmptyResponse = try await client.request(method: "DELETE", endpoint: "staff/\(staffId)/")
    }
}
