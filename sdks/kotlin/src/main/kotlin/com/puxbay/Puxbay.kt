package com.puxbay

import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.coroutines.delay
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import com.puxbay.resources.*
import com.puxbay.models.*

/**
 * Main Puxbay API client with Ktor and coroutines
 */
class Puxbay(
    private val apiKey: String,
    private val baseUrl: String = "https://api.puxbay.com/api/v1",
    private val timeout: Long = 30000,
    private val maxRetries: Int = 3
) {
    init {
        require(apiKey.startsWith("pb_")) { "Invalid API key format. Must start with 'pb_'" }
    }
    
    private val client = HttpClient(CIO) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                isLenient = true
                coerceInputValues = true
            })
        }
        
        install(HttpTimeout) {
            requestTimeoutMillis = timeout
            connectTimeoutMillis = timeout
        }
        
        defaultRequest {
            url(baseUrl)
            header("X-API-Key", apiKey)
            header("Content-Type", "application/json")
            header("User-Agent", "puxbay-kotlin/1.0.0")
            header("Accept-Encoding", "gzip, deflate")
        }
    }
    
    // Resource accessors
    val products = ProductsResource(this)
    val orders = OrdersResource(this)
    val customers = CustomersResource(this)
    val categories = CategoriesResource(this)
    val suppliers = SuppliersResource(this)
    val giftCards = GiftCardsResource(this)
    val branches = BranchesResource(this)
    val staff = StaffResource(this)
    val webhooks = WebhooksResource(this)
    val inventory = InventoryResource(this)
    val reports = ReportsResource(this)
    val purchaseOrders = PurchaseOrdersResource(this)
    val stockTransfers = StockTransfersResource(this)
    val stocktakes = StocktakesResource(this)
    val cashDrawers = CashDrawersResource(this)
    val expenses = ExpensesResource(this)
    val notifications = NotificationsResource(this)
    val returns = ReturnsResource(this)
    
    /**
     * Make HTTP request with retry logic
     */
    suspend inline fun <reified T> request(
        method: HttpMethod,
        endpoint: String,
        body: Any? = null
    ): T {
        var lastException: Exception? = null
        
        repeat(maxRetries + 1) { attempt ->
            try {
                val response: HttpResponse = client.request(endpoint) {
                    this.method = method
                    if (body != null) {
                        setBody(body)
                    }
                }
                
                // Retry on 429 or 5xx
                if (response.status.value == 429 || response.status.value >= 500) {
                    if (attempt < maxRetries) {
                        delay((1000L * (1 shl attempt))) // Exponential backoff
                        return@repeat
                    }
                }
                
                if (!response.status.isSuccess()) {
                    handleErrorResponse(response.status.value, response.bodyAsText())
                }
                
                return if (T::class == Unit::class) {
                    Unit as T
                } else {
                    response.body()
                }
            } catch (e: Exception) {
                lastException = e
                if (attempt < maxRetries) {
                    delay((1000L * (1 shl attempt)))
                }
            }
        }
        
        throw lastException ?: PuxbayException("Unknown error", 0)
    }
    
    private fun handleErrorResponse(statusCode: Int, body: String) {
        val message = try {
            Json.decodeFromString<ErrorResponse>(body).detail ?: "Unknown error"
        } catch (e: Exception) {
            "Unknown error"
        }
        
        when (statusCode) {
            401 -> throw AuthenticationException(message, statusCode)
            429 -> throw RateLimitException(message, statusCode)
            400 -> throw ValidationException(message, statusCode)
            404 -> throw NotFoundException(message, statusCode)
            in 500..599 -> throw ServerException(message, statusCode)
            else -> throw PuxbayException(message, statusCode)
        }
    }
    
    fun close() {
        client.close()
    }
}

// Exceptions
open class PuxbayException(message: String, val statusCode: Int) : Exception(message)
class AuthenticationException(message: String, statusCode: Int) : PuxbayException(message, statusCode)
class RateLimitException(message: String, statusCode: Int) : PuxbayException(message, statusCode)
class ValidationException(message: String, statusCode: Int) : PuxbayException(message, statusCode)
class NotFoundException(message: String, statusCode: Int) : PuxbayException(message, statusCode)
class ServerException(message: String, statusCode: Int) : PuxbayException(message, statusCode)

@Serializable
private data class ErrorResponse(val detail: String? = null, val message: String? = null)
