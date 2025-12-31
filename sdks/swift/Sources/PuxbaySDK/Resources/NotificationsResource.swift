import Foundation

public class NotificationsResource: BaseResource {
    public func list(page: Int = 1) async throws -> PaginatedResponse<Notification> {
        try await client.request(method: "GET", endpoint: "notifications/?page=\(page)")
    }
    
    public func get(notificationId: String) async throws -> Notification {
        try await client.request(method: "GET", endpoint: "notifications/\(notificationId)/")
    }
    
    public func markAsRead(notificationId: String) async throws -> Notification {
        try await client.request(method: "POST", endpoint: "notifications/\(notificationId)/mark-read/")
    }
}
