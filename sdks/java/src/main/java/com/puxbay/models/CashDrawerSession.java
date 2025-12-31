package com.puxbay.models;

import com.google.gson.annotations.SerializedName;

public class CashDrawerSession {
    private String id;
    private String branch;
    
    @SerializedName("opened_by")
    private String openedBy;
    
    @SerializedName("closed_by")
    private String closedBy;
    
    @SerializedName("opening_cash")
    private double openingCash;
    
    @SerializedName("closing_cash")
    private Double closingCash;
    
    @SerializedName("actual_cash")
    private Double actualCash;
    
    private String status;
    
    @SerializedName("opened_at")
    private String openedAt;
    
    @SerializedName("closed_at")
    private String closedAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getBranch() { return branch; }
    public void setBranch(String branch) { this.branch = branch; }
    
    public String getOpenedBy() { return openedBy; }
    public void setOpenedBy(String openedBy) { this.openedBy = openedBy; }
    
    public String getClosedBy() { return closedBy; }
    public void setClosedBy(String closedBy) { this.closedBy = closedBy; }
    
    public double getOpeningCash() { return openingCash; }
    public void setOpeningCash(double openingCash) { this.openingCash = openingCash; }
    
    public Double getClosingCash() { return closingCash; }
    public void setClosingCash(Double closingCash) { this.closingCash = closingCash; }
    
    public Double getActualCash() { return actualCash; }
    public void setActualCash(Double actualCash) { this.actualCash = actualCash; }
    
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    
    public String getOpenedAt() { return openedAt; }
    public void setOpenedAt(String openedAt) { this.openedAt = openedAt; }
    
    public String getClosedAt() { return closedAt; }
    public void setClosedAt(String closedAt) { this.closedAt = closedAt; }
}
