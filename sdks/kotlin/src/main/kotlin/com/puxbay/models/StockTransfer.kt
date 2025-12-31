package com.puxbay.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class StockTransfer(
    val id: String,
    @SerialName("source_branch") val sourceBranch: String,
    @SerialName("source_branch_name") val sourceBranchName: String? = null,
    @SerialName("destination_branch") val destinationBranch: String,
    @SerialName("destination_branch_name") val destinationBranchName: String? = null,
    val status: String,
    val items: List<Map<String, String>>? = null,
    val notes: String? = null,
    @SerialName("created_at") val createdAt: String,
    @SerialName("updated_at") val updatedAt: String
)
