package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.PaginatedResponse;
import com.puxbay.models.GiftCard;
import java.util.HashMap;
import java.util.Map;

public class GiftCardsResource {
    private final Puxbay client;

    public GiftCardsResource(Puxbay client) {
        this.client = client;
    }

    public PaginatedResponse<GiftCard> list(int page, String status) throws PuxbayException {
        String query = "gift-cards/?page=" + page;
        if (status != null) {
            query += "&status=" + status;
        }
        return (PaginatedResponse<GiftCard>) client.request("GET", query, null, PaginatedResponse.class);
    }

    public GiftCard get(String cardId) throws PuxbayException {
        return client.request("GET", "gift-cards/" + cardId + "/", null, GiftCard.class);
    }

    public GiftCard create(GiftCard card) throws PuxbayException {
        return client.request("POST", "gift-cards/", card, GiftCard.class);
    }
    
    public GiftCard redeem(String cardId, double amount) throws PuxbayException {
        Map<String, Object> body = new HashMap<>();
        body.put("amount", amount);
        return client.request("POST", "gift-cards/" + cardId + "/redeem/", body, GiftCard.class);
    }
    
    public Map checkBalance(String code) throws PuxbayException {
        return client.request("GET", "gift-cards/check-balance/?code=" + code, null, Map.class);
    }
}
