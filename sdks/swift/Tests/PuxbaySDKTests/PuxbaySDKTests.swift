import XCTest
@testable import PuxbaySDK

final class PuxbaySDKTests: XCTestCase {
    func testInitialization() {
        let config = PuxbayConfig(apiKey: "pb_test")
        let client = Puxbay(config: config)
        XCTAssertNotNil(client)
        XCTAssertNotNil(client.products)
    }
}
