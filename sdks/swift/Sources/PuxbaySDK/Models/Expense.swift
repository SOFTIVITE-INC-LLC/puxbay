import Foundation

public struct Expense: Codable {
    public let id: String
    public let category: String
    public let description: String
    public let amount: Double
    public let branch: String
    public let receiptUrl: String?
    public let date: String
}
