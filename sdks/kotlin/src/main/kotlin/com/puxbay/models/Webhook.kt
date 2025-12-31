package com.puxbay.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Webhook(
    val id: String,
    val url: String,
    val events: List<String>,
    @SerialName("is_active") val isActive: Boolean,
    val secret: String,
    @SerialName("created_at") val createdAt: String
)
