package com.puxbay.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Expense(
    val id: String,
    val category: String,
    val description: String,
    val amount: Double,
    val branch: String,
    @SerialName("receipt_url") val receiptUrl: String? = null,
    val date: String
)
