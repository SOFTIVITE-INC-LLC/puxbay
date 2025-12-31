import Foundation

public struct Webhook: Codable {
    public let id: String
    public let url: String
    public let events: [String]?
    public let isActive: Bool?
    public let secret: String
    public let createdAt: String
}
