import Foundation

public class ReportsResource: BaseResource {
    // Returning raw Data or specific structs. 
    // Reports are often dynamic.
    
    public struct FinancialSummary: Codable {
        public let totalSales: Double
        public let totalOrders: Int
        // ...
    }
    
    public func financialSummary(startDate: String, endDate: String) async throws -> FinancialSummary {
        try await client.request(method: "GET", endpoint: "reports/financial-summary/?start_date=\(startDate)&end_date=\(endDate)")
    }
    
    // Other reports...
}
