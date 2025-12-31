import Foundation
import PuxbaySDK

@main
struct ListProducts {
    static func main() async {
        guard let apiKey = ProcessInfo.processInfo.environment["PUXBAY_API_KEY"] else {
            print("PUXBAY_API_KEY must be set")
            exit(1)
        }

        let config = PuxbayConfig(apiKey: apiKey)
        let client = Puxbay(config: config)

        print("Fetching products...")
        do {
            let products = try await client.products.list(page: 1)
            for product in products.results {
                print("- \(product.name) ($\(product.price))")
            }
        } catch {
            print("Error: \(error)")
        }
    }
}
