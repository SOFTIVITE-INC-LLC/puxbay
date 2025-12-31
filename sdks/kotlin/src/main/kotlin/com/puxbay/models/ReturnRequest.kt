package com.puxbay.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ReturnRequest(
    val id: String,
    val order: String,
    val status: String,
    val reason: String,
    @SerialName("refund_amount") val refundAmount: Double,
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String
)
