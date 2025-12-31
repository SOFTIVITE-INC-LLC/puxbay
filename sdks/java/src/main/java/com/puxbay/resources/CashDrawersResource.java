package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.PaginatedResponse;
import com.puxbay.models.CashDrawerSession;
import java.util.HashMap;
import java.util.Map;

public class CashDrawersResource {
    private final Puxbay client;

    public CashDrawersResource(Puxbay client) {
        this.client = client;
    }

    public PaginatedResponse<CashDrawerSession> list(int page) throws PuxbayException {
        return (PaginatedResponse<CashDrawerSession>) client.request("GET", "cash-drawers/?page=" + page, null, PaginatedResponse.class);
    }

    public CashDrawerSession get(String drawerId) throws PuxbayException {
        return client.request("GET", "cash-drawers/" + drawerId + "/", null, CashDrawerSession.class);
    }

    public CashDrawerSession open(Map<String, Object> drawerData) throws PuxbayException {
        return client.request("POST", "cash-drawers/", drawerData, CashDrawerSession.class);
    }

    public CashDrawerSession close(String drawerId, double actualCash) throws PuxbayException {
        Map<String, Object> body = new HashMap<>();
        body.put("actual_cash", actualCash);
        return client.request("POST", "cash-drawers/" + drawerId + "/close/", body, CashDrawerSession.class);
    }
}
