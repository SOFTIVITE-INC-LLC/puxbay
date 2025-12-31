package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import java.util.List;
import java.util.Map;

public class ReportsResource {
    private final Puxbay client;

    public ReportsResource(Puxbay client) {
        this.client = client;
    }

    public Map<String, Object> financialSummary(String startDate, String endDate) throws PuxbayException {
        return client.request("GET", "reports/financial-summary/?start_date=" + startDate + "&end_date=" + endDate, null, Map.class);
    }

    public List<Map<String, Object>> dailySales(String startDate, String endDate) throws PuxbayException {
        return client.request("GET", "reports/daily-sales/?start_date=" + startDate + "&end_date=" + endDate, null, List.class);
    }
    
    public List<Map<String, Object>> topProducts(int limit) throws PuxbayException {
        return client.request("GET", "reports/top-products/?limit=" + limit, null, List.class);
    }
    
    public List<Map<String, Object>> lowStock() throws PuxbayException {
        return client.request("GET", "reports/low-stock/", null, List.class);
    }
}
