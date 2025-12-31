import Foundation

open class BaseResource {
    public let client: Puxbay
    
    public init(client: Puxbay) {
        self.client = client
    }
}
