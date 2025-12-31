package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.PaginatedResponse;
import com.puxbay.models.Category;

public class CategoriesResource {
    private final Puxbay client;

    public CategoriesResource(Puxbay client) {
        this.client = client;
    }

    public PaginatedResponse<Category> list(int page) throws PuxbayException {
        return (PaginatedResponse<Category>) client.request("GET", "categories/?page=" + page, null, PaginatedResponse.class);
    }

    public Category get(String categoryId) throws PuxbayException {
        return client.request("GET", "categories/" + categoryId + "/", null, Category.class);
    }

    public Category create(Category category) throws PuxbayException {
        return client.request("POST", "categories/", category, Category.class);
    }

    public Category update(String categoryId, Category category) throws PuxbayException {
        return client.request("PATCH", "categories/" + categoryId + "/", category, Category.class);
    }

    public void delete(String categoryId) throws PuxbayException {
        client.request("DELETE", "categories/" + categoryId + "/", null, Void.class);
    }
}
