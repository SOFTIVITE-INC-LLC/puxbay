import Foundation

public struct ReturnRequest: Codable {
    public let id: String
    public let order: String
    public let status: String
    public let reason: String
    public let refundAmount: Double
    public let createdAt: String
    public let updatedAt: String
}
