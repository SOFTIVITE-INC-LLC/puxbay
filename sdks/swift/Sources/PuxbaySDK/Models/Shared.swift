import Foundation

// Empty response for void returns
public struct EmptyResponse: Codable {}

// Error response
public struct ErrorResponse: Codable {
    public let detail: String?
    public let message: String?
}
