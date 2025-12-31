package com.puxbay.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Customer(
    val id: String,
    val name: String,
    val email: String? = null,
    val phone: String? = null,
    val address: String? = null,
    @SerialName("customer_type") val customerType: String,
    @SerialName("loyalty_points") val loyaltyPoints: Int,
    @SerialName("store_credit_balance") val storeCreditBalance: Double,
    @SerialName("total_spend") val totalSpend: Double,
    val tier: String? = null,
    @SerialName("tier_name") val tierName: String? = null,
    @SerialName("marketing_opt_in") val marketingOptIn: Boolean = false,
    @SerialName("created_at") val createdAt: String
)
