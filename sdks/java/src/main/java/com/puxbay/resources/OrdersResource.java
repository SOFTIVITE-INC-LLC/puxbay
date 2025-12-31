package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.PaginatedResponse;
import com.puxbay.models.Order;

public class OrdersResource {
    private final Puxbay client;

    public OrdersResource(Puxbay client) {
        this.client = client;
    }

    public PaginatedResponse<Order> list(int page, int pageSize) throws PuxbayException {
        // Assuming implementation update in Client to support parameterized types
        return (PaginatedResponse<Order>) client.request("GET", "orders/?page=" + page + "&page_size=" + pageSize, null, PaginatedResponse.class);
    }

    public Order get(String orderId) throws PuxbayException {
        return client.request("GET", "orders/" + orderId + "/", null, Order.class);
    }

    public Order create(Order order) throws PuxbayException {
        return client.request("POST", "orders/", order, Order.class);
    }

    public Order cancel(String orderId) throws PuxbayException {
        client.request("POST", "orders/" + orderId + "/cancel/", null, Void.class);
        return get(orderId);
    }
}
