package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.PaginatedResponse;
import com.puxbay.models.PurchaseOrder;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class PurchaseOrdersResource {
    private final Puxbay client;

    public PurchaseOrdersResource(Puxbay client) {
        this.client = client;
    }

    public PaginatedResponse<PurchaseOrder> list(int page, String status) throws PuxbayException {
        String query = "purchase-orders/?page=" + page;
        if (status != null) query += "&status=" + status;
        return (PaginatedResponse<PurchaseOrder>) client.request("GET", query, null, PaginatedResponse.class);
    }

    public PurchaseOrder get(String poId) throws PuxbayException {
        return client.request("GET", "purchase-orders/" + poId + "/", null, PurchaseOrder.class);
    }

    public PurchaseOrder create(PurchaseOrder po) throws PuxbayException {
        return client.request("POST", "purchase-orders/", po, PurchaseOrder.class);
    }

    public PurchaseOrder update(String poId, PurchaseOrder po) throws PuxbayException {
        return client.request("PATCH", "purchase-orders/" + poId + "/", po, PurchaseOrder.class);
    }

    public PurchaseOrder receive(String poId, List<Map<String, Object>> items) throws PuxbayException {
        Map<String, Object> body = new HashMap<>();
        body.put("items", items);
        return client.request("POST", "purchase-orders/" + poId + "/receive/", body, PurchaseOrder.class);
    }
}
