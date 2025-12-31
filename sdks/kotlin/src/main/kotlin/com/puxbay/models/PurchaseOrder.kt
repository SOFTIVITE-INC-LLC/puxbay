package com.puxbay.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class PurchaseOrder(
    val id: String,
    @SerialName("po_number") val poNumber: String,
    val supplier: String,
    @SerialName("supplier_name") val supplierName: String? = null,
    val status: String,
    @SerialName("total_amount") val totalAmount: Double,
    @SerialName("expected_delivery_date") val expectedDeliveryDate: String? = null,
    val items: List<Map<String, String>>? = null, // Simplified for now, or could be POItem
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String
)
