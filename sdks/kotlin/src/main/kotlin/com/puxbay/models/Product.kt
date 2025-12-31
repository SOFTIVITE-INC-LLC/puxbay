package com.puxbay.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Product(
    val id: String,
    val name: String,
    val sku: String,
    val price: Double,
    @SerialName("stock_quantity") val stockQuantity: Int,
    val description: String? = null,
    val category: String? = null,
    @SerialName("category_name") val categoryName: String? = null,
    @SerialName("is_active") val isActive: Boolean = true,
    @SerialName("low_stock_threshold") val lowStockThreshold: Int? = null,
    @SerialName("cost_price") val costPrice: Double? = null,
    val barcode: String? = null,
    @SerialName("is_composite") val isComposite: Boolean = false,
    @SerialName("created_at") val createdAt: String? = null,
    @SerialName("updated_at") val updatedAt: String? = null
)
