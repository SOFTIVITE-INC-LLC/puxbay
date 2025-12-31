package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.PaginatedResponse;
import com.puxbay.models.Supplier;

public class SuppliersResource {
    private final Puxbay client;

    public SuppliersResource(Puxbay client) {
        this.client = client;
    }

    public PaginatedResponse<Supplier> list(int page, int pageSize) throws PuxbayException {
        return (PaginatedResponse<Supplier>) client.request("GET", "suppliers/?page=" + page + "&page_size=" + pageSize, null, PaginatedResponse.class);
    }

    public Supplier get(String supplierId) throws PuxbayException {
        return client.request("GET", "suppliers/" + supplierId + "/", null, Supplier.class);
    }

    public Supplier create(Supplier supplier) throws PuxbayException {
        return client.request("POST", "suppliers/", supplier, Supplier.class);
    }

    public Supplier update(String supplierId, Supplier supplier) throws PuxbayException {
        return client.request("PATCH", "suppliers/" + supplierId + "/", supplier, Supplier.class);
    }

    public void delete(String supplierId) throws PuxbayException {
        client.request("DELETE", "suppliers/" + supplierId + "/", null, Void.class);
    }
}
