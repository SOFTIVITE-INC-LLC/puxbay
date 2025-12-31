package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.PaginatedResponse;
import com.puxbay.models.Stocktake;

public class StocktakesResource {
    private final Puxbay client;

    public StocktakesResource(Puxbay client) {
        this.client = client;
    }

    public PaginatedResponse<Stocktake> list(int page) throws PuxbayException {
        return (PaginatedResponse<Stocktake>) client.request("GET", "stocktakes/?page=" + page, null, PaginatedResponse.class);
    }

    public Stocktake get(String stocktakeId) throws PuxbayException {
        return client.request("GET", "stocktakes/" + stocktakeId + "/", null, Stocktake.class);
    }

    public Stocktake create(Stocktake stocktake) throws PuxbayException {
        return client.request("POST", "stocktakes/", stocktake, Stocktake.class);
    }

    public Stocktake complete(String stocktakeId) throws PuxbayException {
        return client.request("POST", "stocktakes/" + stocktakeId + "/complete/", null, Stocktake.class);
    }
}
