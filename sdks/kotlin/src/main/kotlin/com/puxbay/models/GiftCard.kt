package com.puxbay.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class GiftCard(
    val id: String,
    val code: String,
    val balance: Double,
    val status: String,
    @SerialName("expiry_date") val expiryDate: String? = null
)
