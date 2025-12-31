import Foundation

public struct Branch: Codable {
    public let id: String
    public let name: String
    public let uniqueId: String
    public let address: String?
    public let phone: String?
    public let branchType: String
    public let currencyCode: String
    public let currencySymbol: String
    public let lowStockThreshold: Int
    public let createdAt: String
    public let updatedAt: String
}
