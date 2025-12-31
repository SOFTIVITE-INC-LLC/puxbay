import Foundation

public struct Product: Codable {
    public let id: String
    public let name: String
    public let sku: String
    public let price: Double
    public let stockQuantity: Int
    public let description: String?
    public let category: String?
    public let categoryName: String?
    public let isActive: Bool?
    public let lowStockThreshold: Int?
    public let costPrice: Double?
    public let barcode: String?
    public let isComposite: Bool?
    public let createdAt: String?
    public let updatedAt: String?
}
