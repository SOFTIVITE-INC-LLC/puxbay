import Foundation

public struct Customer: Codable {
    public let id: String
    public let name: String
    public let email: String?
    public let phone: String?
    public let address: String?
    public let customerType: String
    public let loyaltyPoints: Int
    public let storeCreditBalance: Double
    public let totalSpend: Double
    public let tier: String?
    public let tierName: String?
    public let marketingOptIn: Bool?
    public let createdAt: String
}
