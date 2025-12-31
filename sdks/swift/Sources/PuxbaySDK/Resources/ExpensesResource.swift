import Foundation

public class ExpensesResource: BaseResource {
    public func list(page: Int = 1, category: String? = nil) async throws -> PaginatedResponse<Expense> {
        var query = "page=\(page)"
        if let category = category {
            query += "&category=\(category)"
        }
        return try await client.request(method: "GET", endpoint: "expenses/?\(query)")
    }
    
    public func get(expenseId: String) async throws -> Expense {
        try await client.request(method: "GET", endpoint: "expenses/\(expenseId)/")
    }
    
    public func create(expense: Expense) async throws -> Expense {
        try await client.request(method: "POST", endpoint: "expenses/", body: expense)
    }
    
    public func update(expenseId: String, expense: Expense) async throws -> Expense {
        try await client.request(method: "PATCH", endpoint: "expenses/\(expenseId)/", body: expense)
    }
    
    public func delete(expenseId: String) async throws {
        let _: EmptyResponse = try await client.request(method: "DELETE", endpoint: "expenses/\(expenseId)/")
    }
    
    public func listCategories() async throws -> [String] {
        try await client.request(method: "GET", endpoint: "expense-categories/")
    }
}
