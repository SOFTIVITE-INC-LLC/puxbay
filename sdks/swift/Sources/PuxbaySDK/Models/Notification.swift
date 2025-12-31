import Foundation

public struct Notification: Codable {
    public let id: String
    public let title: String
    public let message: String
    public let isRead: Bool
    public let notificationType: String
    public let createdAt: String
}
