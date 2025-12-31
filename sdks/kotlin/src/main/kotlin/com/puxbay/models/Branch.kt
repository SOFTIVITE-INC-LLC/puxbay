package com.puxbay.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Branch(
    val id: String,
    val name: String,
    @SerialName("unique_id") val uniqueId: String,
    val address: String? = null,
    val phone: String? = null,
    @SerialName("branch_type") val branchType: String,
    @SerialName("currency_code") val currencyCode: String,
    @SerialName("currency_symbol") val currencySymbol: String,
    @SerialName("low_stock_threshold") val lowStockThreshold: Int,
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String
)
