import Foundation

public struct PaginatedResponse<T: Codable>: Codable {
    public let count: Int
    public let next: String?
    public let previous: String?
    public let results: [T]
}
