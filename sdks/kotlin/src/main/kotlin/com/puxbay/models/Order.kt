package com.puxbay.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Order(
    val id: String,
    @SerialName("order_number") val orderNumber: String,
    val status: String,
    val subtotal: Double,
    @SerialName("tax_amount") val taxAmount: Double,
    @SerialName("total_amount") val totalAmount: Double,
    @SerialName("amount_paid") val amountPaid: Double,
    @SerialName("payment_method") val paymentMethod: String,
    @SerialName("ordering_type") val orderingType: String,
    @SerialName("offline_uuid") val offlineUuid: String? = null,
    val customer: String? = null,
    @SerialName("customer_name") val customerName: String? = null,
    val cashier: String? = null,
    @SerialName("cashier_name") val cashierName: String? = null,
    val branch: String,
    @SerialName("branch_name") val branchName: String,
    val items: List<OrderItem> = emptyList(),
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String
)

@Serializable
data class OrderItem(
    val id: String,
    val product: String,
    @SerialName("product_name") val productName: String,
    val sku: String,
    @SerialName("item_number") val itemNumber: String,
    val quantity: Int,
    val price: Double,
    @SerialName("cost_price") val costPrice: Double? = null,
    @SerialName("get_total_item_price") val totalPrice: Double
)
