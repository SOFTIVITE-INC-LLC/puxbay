package com.puxbay.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class Order {
    private String id;
    
    @SerializedName("order_number")
    private String orderNumber;
    
    private String status;
    private double subtotal;
    
    @SerializedName("tax_amount")
    private double taxAmount;
    
    @SerializedName("total_amount")
    private double totalAmount;
    
    @SerializedName("amount_paid")
    private double amountPaid;
    
    @SerializedName("payment_method")
    private String paymentMethod;
    
    @SerializedName("ordering_type")
    private String orderingType;
    
    @SerializedName("offline_uuid")
    private String offlineUuid;
    
    private String customer;
    
    @SerializedName("customer_name")
    private String customerName;
    
    private String cashier;
    
    @SerializedName("cashier_name")
    private String cashierName;
    
    private String branch;
    
    @SerializedName("branch_name")
    private String branchName;
    
    private List<OrderItem> items;
    
    @SerializedName("created_at")
    private String createdAt;
    
    @SerializedName("updated_at")
    private String updatedAt;

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getOrderNumber() { return orderNumber; }
    public void setOrderNumber(String orderNumber) { this.orderNumber = orderNumber; }
    
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    
    public double getSubtotal() { return subtotal; }
    public void setSubtotal(double subtotal) { this.subtotal = subtotal; }
    
    public double getTaxAmount() { return taxAmount; }
    public void setTaxAmount(double taxAmount) { this.taxAmount = taxAmount; }
    
    public double getTotalAmount() { return totalAmount; }
    public void setTotalAmount(double totalAmount) { this.totalAmount = totalAmount; }
    
    public double getAmountPaid() { return amountPaid; }
    public void setAmountPaid(double amountPaid) { this.amountPaid = amountPaid; }
    
    public String getPaymentMethod() { return paymentMethod; }
    public void setPaymentMethod(String paymentMethod) { this.paymentMethod = paymentMethod; }
    
    public String getOrderingType() { return orderingType; }
    public void setOrderingType(String orderingType) { this.orderingType = orderingType; }
    
    public String getOfflineUuid() { return offlineUuid; }
    public void setOfflineUuid(String offlineUuid) { this.offlineUuid = offlineUuid; }
    
    public String getCustomer() { return customer; }
    public void setCustomer(String customer) { this.customer = customer; }
    
    public String getCustomerName() { return customerName; }
    public void setCustomerName(String customerName) { this.customerName = customerName; }
    
    public String getCashier() { return cashier; }
    public void setCashier(String cashier) { this.cashier = cashier; }
    
    public String getCashierName() { return cashierName; }
    public void setCashierName(String cashierName) { this.cashierName = cashierName; }
    
    public String getBranch() { return branch; }
    public void setBranch(String branch) { this.branch = branch; }
    
    public String getBranchName() { return branchName; }
    public void setBranchName(String branchName) { this.branchName = branchName; }
    
    public List<OrderItem> getItems() { return items; }
    public void setItems(List<OrderItem> items) { this.items = items; }
    
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    
    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
}
