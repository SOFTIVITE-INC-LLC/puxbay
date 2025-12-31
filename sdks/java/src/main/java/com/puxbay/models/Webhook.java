package com.puxbay.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class Webhook {
    private String id;
    private String url;
    private List<String> events;
    
    @SerializedName("is_active")
    private Boolean isActive;
    
    private String secret;
    
    @SerializedName("created_at")
    private String createdAt;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getUrl() { return url; }
    public void setUrl(String url) { this.url = url; }
    
    public List<String> getEvents() { return events; }
    public void setEvents(List<String> events) { this.events = events; }
    
    public Boolean getIsActive() { return isActive; }
    public void setIsActive(Boolean isActive) { this.isActive = isActive; }
    
    public String getSecret() { return secret; }
    public void setSecret(String secret) { this.secret = secret; }
    
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
}
