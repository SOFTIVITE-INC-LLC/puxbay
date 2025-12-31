package com.puxbay.models;

import com.google.gson.annotations.SerializedName;

public class Customer {
    private String id;
    private String name;
    private String email;
    private String phone;
    private String address;
    
    @SerializedName("customer_type")
    private String customerType;
    
    @SerializedName("loyalty_points")
    private int loyaltyPoints;
    
    @SerializedName("store_credit_balance")
    private double storeCreditBalance;
    
    @SerializedName("total_spend")
    private double totalSpend;
    
    private String tier;
    
    @SerializedName("tier_name")
    private String tierName;
    
    @SerializedName("marketing_opt_in")
    private boolean marketingOptIn;
    
    @SerializedName("created_at")
    private String createdAt;

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    
    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }
    
    public String getAddress() { return address; }
    public void setAddress(String address) { this.address = address; }
    
    public String getCustomerType() { return customerType; }
    public void setCustomerType(String customerType) { this.customerType = customerType; }
    
    public int getLoyaltyPoints() { return loyaltyPoints; }
    public void setLoyaltyPoints(int loyaltyPoints) { this.loyaltyPoints = loyaltyPoints; }
    
    public double getStoreCreditBalance() { return storeCreditBalance; }
    public void setStoreCreditBalance(double storeCreditBalance) { this.storeCreditBalance = storeCreditBalance; }
    
    public double getTotalSpend() { return totalSpend; }
    public void setTotalSpend(double totalSpend) { this.totalSpend = totalSpend; }
    
    public String getTier() { return tier; }
    public void setTier(String tier) { this.tier = tier; }
    
    public String getTierName() { return tierName; }
    public void setTierName(String tierName) { this.tierName = tierName; }
    
    public boolean isMarketingOptIn() { return marketingOptIn; }
    public void setMarketingOptIn(boolean marketingOptIn) { this.marketingOptIn = marketingOptIn; }
    
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
}
