import Foundation

public struct Staff: Codable {
    public let id: String
    public let username: String
    public let fullName: String
    public let email: String
    public let role: String
    public let branch: String?
    public let branchName: String?
}
