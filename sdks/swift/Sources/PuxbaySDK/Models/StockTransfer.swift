import Foundation

public struct StockTransfer: Codable {
    public let id: String
    public let sourceBranch: String
    public let sourceBranchName: String?
    public let destinationBranch: String
    public let destinationBranchName: String?
    public let status: String
    public let items: [[String: String]]?
    public let notes: String?
    public let createdAt: String
    public let updatedAt: String
}
