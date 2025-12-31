package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.PaginatedResponse;
import com.puxbay.models.Customer;

public class CustomersResource {
    private final Puxbay client;

    public CustomersResource(Puxbay client) {
        this.client = client;
    }

    public PaginatedResponse<Customer> list(int page, int pageSize) throws PuxbayException {
        return (PaginatedResponse<Customer>) client.request("GET", "customers/?page=" + page + "&page_size=" + pageSize, null, PaginatedResponse.class);
    }

    public Customer get(String customerId) throws PuxbayException {
        return client.request("GET", "customers/" + customerId + "/", null, Customer.class);
    }

    public Customer create(Customer customer) throws PuxbayException {
        return client.request("POST", "customers/", customer, Customer.class);
    }

    public Customer update(String customerId, Customer customer) throws PuxbayException {
        return client.request("PATCH", "customers/" + customerId + "/", customer, Customer.class);
    }

    public void delete(String customerId) throws PuxbayException {
        client.request("DELETE", "customers/" + customerId + "/", null, Void.class);
    }
}
