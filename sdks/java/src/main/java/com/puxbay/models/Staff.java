package com.puxbay.models;

import com.google.gson.annotations.SerializedName;

public class Staff {
    private String id;
    private String username;
    
    @SerializedName("full_name")
    private String fullName;
    
    private String email;
    private String role;
    private String branch;
    
    @SerializedName("branch_name")
    private String branchName;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    
    public String getFullName() { return fullName; }
    public void setFullName(String fullName) { this.fullName = fullName; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    
    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }
    
    public String getBranch() { return branch; }
    public void setBranch(String branch) { this.branch = branch; }
    
    public String getBranchName() { return branchName; }
    public void setBranchName(String branchName) { this.branchName = branchName; }
}
