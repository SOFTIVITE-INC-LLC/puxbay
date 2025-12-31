import Foundation

public struct GiftCard: Codable {
    public let id: String
    public let code: String
    public let balance: Double
    public let status: String
    public let expiryDate: String?
}
