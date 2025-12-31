package com.puxbay.models;

import com.google.gson.annotations.SerializedName;

public class OrderItem {
    private String id;
    private String product;
    
    @SerializedName("product_name")
    private String productName;
    
    private String sku;
    
    @SerializedName("item_number")
    private String itemNumber;
    
    private int quantity;
    private double price;
    
    @SerializedName("cost_price")
    private Double costPrice;
    
    @SerializedName("total_price")
    private double totalPrice;

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getProduct() { return product; }
    public void setProduct(String product) { this.product = product; }
    
    public String getProductName() { return productName; }
    public void setProductName(String productName) { this.productName = productName; }
    
    public String getSku() { return sku; }
    public void setSku(String sku) { this.sku = sku; }
    
    public String getItemNumber() { return itemNumber; }
    public void setItemNumber(String itemNumber) { this.itemNumber = itemNumber; }
    
    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }
    
    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }
    
    public Double getCostPrice() { return costPrice; }
    public void setCostPrice(Double costPrice) { this.costPrice = costPrice; }
    
    public double getTotalPrice() { return totalPrice; }
    public void setTotalPrice(double totalPrice) { this.totalPrice = totalPrice; }
}
