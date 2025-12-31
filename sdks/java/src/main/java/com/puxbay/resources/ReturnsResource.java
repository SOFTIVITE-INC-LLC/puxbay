package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.PaginatedResponse;
import com.puxbay.models.ReturnRequest;

public class ReturnsResource {
    private final Puxbay client;

    public ReturnsResource(Puxbay client) {
        this.client = client;
    }

    public PaginatedResponse<ReturnRequest> list(int page) throws PuxbayException {
        return (PaginatedResponse<ReturnRequest>) client.request("GET", "returns/?page=" + page, null, PaginatedResponse.class);
    }

    public ReturnRequest get(String returnId) throws PuxbayException {
        return client.request("GET", "returns/" + returnId + "/", null, ReturnRequest.class);
    }

    public ReturnRequest create(ReturnRequest returnData) throws PuxbayException {
        return client.request("POST", "returns/", returnData, ReturnRequest.class);
    }
    
    public ReturnRequest approve(String returnId) throws PuxbayException {
        return client.request("POST", "returns/" + returnId + "/approve/", null, ReturnRequest.class);
    }
}
