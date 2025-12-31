package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.PaginatedResponse;
import com.puxbay.models.StockTransfer;

public class StockTransfersResource {
    private final Puxbay client;

    public StockTransfersResource(Puxbay client) {
        this.client = client;
    }

    public PaginatedResponse<StockTransfer> list(int page, String status) throws PuxbayException {
        String query = "stock-transfers/?page=" + page;
        if (status != null) query += "&status=" + status;
        return (PaginatedResponse<StockTransfer>) client.request("GET", query, null, PaginatedResponse.class);
    }

    public StockTransfer get(String transferId) throws PuxbayException {
        return client.request("GET", "stock-transfers/" + transferId + "/", null, StockTransfer.class);
    }

    public StockTransfer create(StockTransfer transfer) throws PuxbayException {
        return client.request("POST", "stock-transfers/", transfer, StockTransfer.class);
    }

    public StockTransfer complete(String transferId) throws PuxbayException {
        return client.request("POST", "stock-transfers/" + transferId + "/complete/", null, StockTransfer.class);
    }
}
