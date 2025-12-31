package com.puxbay.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class CashDrawerSession(
    val id: String,
    val branch: String,
    @SerialName("opened_by") val openedBy: String,
    @SerialName("closed_by") val closedBy: String? = null,
    @SerialName("opening_cash") val openingCash: Double,
    @SerialName("closing_cash") val closingCash: Double? = null,
    @SerialName("actual_cash") val actualCash: Double? = null,
    val status: String,
    @SerialName("opened_at") val openedAt: String,
    @SerialName("closed_at") val closedAt: String? = null
)
