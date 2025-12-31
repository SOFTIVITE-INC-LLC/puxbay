package com.puxbay.resources

import com.puxbay.Puxbay
import com.puxbay.models.Expense
import com.puxbay.models.PaginatedResponse
import io.ktor.http.HttpMethod

class ExpensesResource(client: Puxbay) : BaseResource(client) {
    suspend fun list(page: Int = 1, category: String? = null): PaginatedResponse<Expense> {
        val catParam = if (category != null) "&category=$category" else ""
        return client.request(HttpMethod.Get, "expenses/?page=$page$catParam")
    }
    
    suspend fun get(expenseId: String): Expense =
        client.request(HttpMethod.Get, "expenses/$expenseId/")
    
    suspend fun create(expense: Expense): Expense =
        client.request(HttpMethod.Post, "expenses/", expense)
    
    suspend fun update(expenseId: String, expense: Expense): Expense =
        client.request(HttpMethod.Patch, "expenses/$expenseId/", expense)
    
    suspend fun delete(expenseId: String) {
        client.request<Unit>(HttpMethod.Delete, "expenses/$expenseId/")
    }
    
    suspend fun listCategories(): List<String> =
        client.request(HttpMethod.Get, "expense-categories/")
}
