package com.puxbay.models;

import com.google.gson.annotations.SerializedName;

public class Expense {
    private String id;
    private String category;
    private String description;
    private double amount;
    private String branch;
    
    @SerializedName("receipt_url")
    private String receiptUrl;
    
    private String date;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    
    public double getAmount() { return amount; }
    public void setAmount(double amount) { this.amount = amount; }
    
    public String getBranch() { return branch; }
    public void setBranch(String branch) { this.branch = branch; }
    
    public String getReceiptUrl() { return receiptUrl; }
    public void setReceiptUrl(String receiptUrl) { this.receiptUrl = receiptUrl; }
    
    public String getDate() { return date; }
    public void setDate(String date) { this.date = date; }
}
