import Foundation

public struct Supplier: Codable {
    public let id: String
    public let name: String
    public let contactPerson: String?
    public let email: String?
    public let phone: String?
    public let address: String?
    public let createdAt: String
}
