import Foundation

public class CashDrawersResource: BaseResource {
    public func list(page: Int = 1) async throws -> PaginatedResponse<CashDrawerSession> {
        try await client.request(method: "GET", endpoint: "cash-drawers/?page=\(page)")
    }
    
    public func get(drawerId: String) async throws -> CashDrawerSession {
        try await client.request(method: "GET", endpoint: "cash-drawers/\(drawerId)/")
    }
    
    public func open(drawerData: [String: Double]) async throws -> CashDrawerSession {
        // Assuming body is simple [String: Double] for opening_cash etc.
        // Actually [String: Any] but values are doubles/strings.
        // Swift requires concrete types for Codable.
        struct OpenBody: Codable {
             let openingCash: Double
             // Add other fields if needed
        }
        // Assuming keys snake_case conversion handled by encoder
        // But dictionary keys aren't converted automatically by keyEncodingStrategy usually, only Struct keys.
        // So I'll use a Struct or custom encoding.
        // I'll define OpenBody properly with explicit CodingKeys if needed or rely on converter.
        // JSONEncoder().keyEncodingStrategy = .convertToSnakeCase applies to Struct properties.
        return try await client.request(method: "POST", endpoint: "cash-drawers/", body: drawerData) 
        // Note: [String: Double] is Encodable but keys won't be converted to snake_case automatically if they are strings in a dict.
        // If API expects "opening_cash", I must provide "opening_cash" key in dict or use struct.
        // I'll assume caller passes correct keys or use struct.
        // Given I'm enforcing strictness, I should defined a struct.
        // But signature says `[String: Double]`. I'll stick to it.
        // Actually, previous code used `[String: Any]`.
    }
    
    public func close(drawerId: String, actualCash: Double) async throws -> CashDrawerSession {
        struct CloseBody: Codable {
            let actualCash: Double
        }
        return try await client.request(method: "POST", endpoint: "cash-drawers/\(drawerId)/close/", body: CloseBody(actualCash: actualCash))
    }
}
