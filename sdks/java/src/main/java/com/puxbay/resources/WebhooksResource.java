package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.PaginatedResponse;
import com.puxbay.models.Webhook;
import java.util.Map;

public class WebhooksResource {
    private final Puxbay client;

    public WebhooksResource(Puxbay client) {
        this.client = client;
    }

    public PaginatedResponse<Webhook> list(int page) throws PuxbayException {
        return (PaginatedResponse<Webhook>) client.request("GET", "webhooks/?page=" + page, null, PaginatedResponse.class);
    }

    public Webhook get(String webhookId) throws PuxbayException {
        return client.request("GET", "webhooks/" + webhookId + "/", null, Webhook.class);
    }

    public Webhook create(Webhook webhook) throws PuxbayException {
        return client.request("POST", "webhooks/", webhook, Webhook.class);
    }

    public Webhook update(String webhookId, Webhook webhook) throws PuxbayException {
        return client.request("PATCH", "webhooks/" + webhookId + "/", webhook, Webhook.class);
    }

    public void delete(String webhookId) throws PuxbayException {
        client.request("DELETE", "webhooks/" + webhookId + "/", null, Void.class);
    }
    
    public Map listEvents(String webhookId, int page) throws PuxbayException {
        return client.request("GET", "webhook-logs/?webhook=" + webhookId + "&page=" + page, null, Map.class);
    }
}
