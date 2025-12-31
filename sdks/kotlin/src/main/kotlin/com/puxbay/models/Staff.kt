package com.puxbay.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class Staff(
    val id: String,
    val username: String,
    @SerialName("full_name") val fullName: String,
    val email: String,
    val role: String,
    val branch: String? = null,
    @SerialName("branch_name") val branchName: String? = null
)
