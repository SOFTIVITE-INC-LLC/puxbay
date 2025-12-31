package com.puxbay.resources

import com.puxbay.Puxbay
import io.ktor.http.HttpMethod

class ReportsResource(client: Puxbay) : BaseResource(client) {
    suspend fun financialSummary(startDate: String, endDate: String): Map<String, Any> =
        client.request(HttpMethod.Get, "reports/financial-summary/?start_date=$startDate&end_date=$endDate")
    
    suspend fun dailySales(startDate: String, endDate: String): List<Map<String, Any>> =
        client.request(HttpMethod.Get, "reports/daily-sales/?start_date=$startDate&end_date=$endDate")
        
    suspend fun topProducts(limit: Int = 10): List<Map<String, Any>> =
        client.request(HttpMethod.Get, "reports/top-products/?limit=$limit")
        
    suspend fun lowStock(): List<Map<String, Any>> =
        client.request(HttpMethod.Get, "reports/low-stock/")
}
