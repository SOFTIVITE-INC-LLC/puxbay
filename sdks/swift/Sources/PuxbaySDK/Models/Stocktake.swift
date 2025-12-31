import Foundation

public struct Stocktake: Codable {
    public let id: String
    public let branch: String
    public let status: String
    public let notes: String?
    public let createdAt: String
    public let updatedAt: String
}
