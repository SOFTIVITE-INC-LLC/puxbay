package com.puxbay.models;

import com.google.gson.annotations.SerializedName;

public class GiftCard {
    private String id;
    private String code;
    private double balance;
    private String status;
    
    @SerializedName("expiry_date")
    private String expiryDate;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }
    
    public double getBalance() { return balance; }
    public void setBalance(double balance) { this.balance = balance; }
    
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    
    public String getExpiryDate() { return expiryDate; }
    public void setExpiryDate(String expiryDate) { this.expiryDate = expiryDate; }
}
