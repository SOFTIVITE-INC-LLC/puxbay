import Foundation

public struct PurchaseOrder: Codable {
    public let id: String
    public let poNumber: String
    public let supplier: String
    public let supplierName: String?
    public let status: String
    public let totalAmount: Double
    public let expectedDeliveryDate: String?
    public let items: [[String: String]]? // Or explicit POItem struct if we knew structure perfectly
    public let createdAt: String
    public let updatedAt: String
}
