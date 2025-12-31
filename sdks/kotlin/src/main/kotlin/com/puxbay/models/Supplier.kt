package com.puxbay.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Supplier(
    val id: String,
    val name: String,
    @SerialName("contact_person") val contactPerson: String? = null,
    val email: String? = null,
    val phone: String? = null,
    val address: String? = null,
    @SerialName("created_at") val createdAt: String
)
