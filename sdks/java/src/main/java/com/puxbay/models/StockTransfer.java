package com.puxbay.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;
import java.util.Map;

public class StockTransfer {
    private String id;
    
    @SerializedName("source_branch")
    private String sourceBranch;
    
    @SerializedName("source_branch_name")
    private String sourceBranchName;
    
    @SerializedName("destination_branch")
    private String destinationBranch;
    
    @SerializedName("destination_branch_name")
    private String destinationBranchName;
    
    private String status;
    private List<Map<String, Object>> items;
    private String notes;
    
    @SerializedName("created_at")
    private String createdAt;
    
    @SerializedName("updated_at")
    private String updatedAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getSourceBranch() { return sourceBranch; }
    public void setSourceBranch(String sourceBranch) { this.sourceBranch = sourceBranch; }
    
    public String getSourceBranchName() { return sourceBranchName; }
    public void setSourceBranchName(String sourceBranchName) { this.sourceBranchName = sourceBranchName; }
    
    public String getDestinationBranch() { return destinationBranch; }
    public void setDestinationBranch(String destinationBranch) { this.destinationBranch = destinationBranch; }
    
    public String getDestinationBranchName() { return destinationBranchName; }
    public void setDestinationBranchName(String destinationBranchName) { this.destinationBranchName = destinationBranchName; }
    
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    
    public List<Map<String, Object>> getItems() { return items; }
    public void setItems(List<Map<String, Object>> items) { this.items = items; }
    
    public String getNotes() { return notes; }
    public void setNotes(String notes) { this.notes = notes; }
    
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    
    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
}
