package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.PaginatedResponse;
import com.puxbay.models.Notification;

public class NotificationsResource {
    private final Puxbay client;

    public NotificationsResource(Puxbay client) {
        this.client = client;
    }

    public PaginatedResponse<Notification> list(int page) throws PuxbayException {
        return (PaginatedResponse<Notification>) client.request("GET", "notifications/?page=" + page, null, PaginatedResponse.class);
    }

    public Notification get(String notificationId) throws PuxbayException {
        return client.request("GET", "notifications/" + notificationId + "/", null, Notification.class);
    }

    public Notification markAsRead(String notificationId) throws PuxbayException {
        return client.request("POST", "notifications/" + notificationId + "/mark-read/", null, Notification.class);
    }
}
