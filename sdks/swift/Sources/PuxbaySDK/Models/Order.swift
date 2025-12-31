import Foundation

public struct Order: Codable {
    public let id: String
    public let orderNumber: String
    public let status: String
    public let subtotal: Double
    public let taxAmount: Double
    public let totalAmount: Double
    public let amountPaid: Double
    public let paymentMethod: String
    public let orderingType: String
    public let offlineUuid: String?
    public let customer: String?
    public let customerName: String?
    public let cashier: String?
    public let cashierName: String?
    public let branch: String
    public let branchName: String
    public let items: [OrderItem]?
    public let createdAt: String
    public let updatedAt: String
}

public struct OrderItem: Codable {
    public let id: String
    public let product: String
    public let productName: String
    public let sku: String
    public let itemNumber: String
    public let quantity: Int
    public let price: Double
    public let costPrice: Double?
    public let getTotalItemPrice: Double? // Computed field in API maybe?
}
