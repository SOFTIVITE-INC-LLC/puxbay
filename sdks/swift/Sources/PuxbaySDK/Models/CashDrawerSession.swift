import Foundation

public struct CashDrawerSession: Codable {
    public let id: String
    public let branch: String
    public let openedBy: String
    public let closedBy: String?
    public let openingCash: Double
    public let closingCash: Double?
    public let actualCash: Double?
    public let status: String
    public let openedAt: String
    public let closedAt: String?
}
