package com.puxbay.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Notification(
    val id: String,
    val title: String,
    val message: String,
    @SerialName("is_read") val isRead: Boolean,
    @SerialName("notification_type") val notificationType: String,
    @SerialName("created_at") val createdAt: String
)
