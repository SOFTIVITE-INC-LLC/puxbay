package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import java.util.List;
import java.util.Map;

public class InventoryResource {
    private final Puxbay client;

    public InventoryResource(Puxbay client) {
        this.client = client;
    }

    public List<Map<String, Object>> getStockLevels(String branchId) throws PuxbayException {
        // Assuming Response wrapper with results
        Map response = client.request("GET", "inventory/stock-levels/?branch=" + branchId, null, Map.class);
        return (List<Map<String, Object>>) response.get("results");
    }

    public Map<String, Object> getProductStock(String productId, String branchId) throws PuxbayException {
        return client.request("GET", "inventory/product-stock/?product=" + productId + "&branch=" + branchId, null, Map.class);
    }
}
