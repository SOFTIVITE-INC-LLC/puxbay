import Foundation

/// Main Puxbay API client with URLSession and retry logic
public class Puxbay {
    private let apiKey: String
    private let baseURL: URL
    private let session: URLSession
    private let maxRetries: Int
    
    /// Initialize Puxbay client
    /// - Parameters:
    ///   - apiKey: API key (must start with 'pb_')
    ///   - baseURL: Base URL for API (default: https://api.puxbay.com/api/v1)
    ///   - timeout: Request timeout in seconds (default: 30)
    ///   - maxRetries: Maximum retry attempts (default: 3)
    public init(
        apiKey: String,
        baseURL: String = "https://api.puxbay.com/api/v1",
        timeout: TimeInterval = 30,
        maxRetries: Int = 3
    ) throws {
        guard apiKey.hasPrefix("pb_") else {
            throw PuxbayError.invalidAPIKey
        }
        
        guard let url = URL(string: baseURL) else {
            throw PuxbayError.invalidBaseURL
        }
        
        self.apiKey = apiKey
        self.baseURL = url
        self.maxRetries = maxRetries
        
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = timeout
        config.httpAdditionalHeaders = [
            "X-API-Key": apiKey,
            "Content-Type": "application/json",
            "User-Agent": "puxbay-swift/1.0.0",
            "Accept-Encoding": "gzip, deflate"
        ]
        config.requestCachePolicy = .reloadIgnoringLocalCacheData
        config.urlCache = nil
        
        self.session = URLSession(configuration: config)
    }
    
    // Resource accessors
    public lazy var products = ProductsResource(client: self)
    public lazy var orders = OrdersResource(client: self)
    public lazy var customers = CustomersResource(client: self)
    public lazy var categories = CategoriesResource(client: self)
    public lazy var suppliers = SuppliersResource(client: self)
    public lazy var giftCards = GiftCardsResource(client: self)
    public lazy var branches = BranchesResource(client: self)
    public lazy var staff = StaffResource(client: self)
    public lazy var webhooks = WebhooksResource(client: self)
    public lazy var inventory = InventoryResource(client: self)
    public lazy var reports = ReportsResource(client: self)
    public lazy var purchaseOrders = PurchaseOrdersResource(client: self)
    public lazy var stockTransfers = StockTransfersResource(client: self)
    public lazy var stocktakes = StocktakesResource(client: self)
    public lazy var cashDrawers = CashDrawersResource(client: self)
    public lazy var expenses = ExpensesResource(client: self)
    public lazy var notifications = NotificationsResource(client: self)
    public lazy var returns = ReturnsResource(client: self)
    
    /// Make HTTP request with retry logic
    func request<T: Decodable>(
        method: String,
        endpoint: String,
        body: Encodable? = nil
    ) async throws -> T {
        var lastError: Error?
        
        for attempt in 0...maxRetries {
            do {
                let url = baseURL.appendingPathComponent(endpoint)
                var request = URLRequest(url: url)
                request.httpMethod = method
                
                if let body = body {
                    let encoder = JSONEncoder()
                    encoder.keyEncodingStrategy = .convertToSnakeCase
                    request.httpBody = try encoder.encode(body)
                }
                
                let (data, response) = try await session.data(for: request)
                
                guard let httpResponse = response as? HTTPURLResponse else {
                    throw PuxbayError.invalidResponse
                }
                
                // Retry on 429 or 5xx
                if httpResponse.statusCode == 429 || httpResponse.statusCode >= 500 {
                    if attempt < maxRetries {
                        let delay = pow(2.0, Double(attempt))
                        try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                        continue
                    }
                }
                
                guard (200...299).contains(httpResponse.statusCode) else {
                    try handleErrorResponse(statusCode: httpResponse.statusCode, data: data)
                }
                
                if T.self == EmptyResponse.self {
                    return EmptyResponse() as! T
                }
                
                let decoder = JSONDecoder()
                decoder.keyDecodingStrategy = .convertFromSnakeCase
                return try decoder.decode(T.self, from: data)
            } catch {
                lastError = error
                if attempt < maxRetries {
                    let delay = pow(2.0, Double(attempt))
                    try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                }
            }
        }
        
        throw lastError ?? PuxbayError.unknownError
    }
    
    private func handleErrorResponse(statusCode: Int, data: Data) throws {
        let message: String
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        
        if let errorResponse = try? decoder.decode(ErrorResponse.self, from: data) {
            message = errorResponse.detail ?? errorResponse.message ?? "Unknown error"
        } else {
            message = "Unknown error"
        }
        
        switch statusCode {
        case 401:
            throw PuxbayError.authenticationError(message)
        case 429:
            throw PuxbayError.rateLimitError(message)
        case 400:
            throw PuxbayError.validationError(message)
        case 404:
            throw PuxbayError.notFoundError(message)
        case 500...:
            throw PuxbayError.serverError(message)
        default:
            throw PuxbayError.apiError(message, statusCode)
        }
    }
}

// MARK: - Error Types

public enum PuxbayError: Error {
    case invalidAPIKey
    case invalidBaseURL
    case invalidResponse
    case authenticationError(String)
    case rateLimitError(String)
    case validationError(String)
    case notFoundError(String)
    case serverError(String)
    case apiError(String, Int)
    case unknownError
}
