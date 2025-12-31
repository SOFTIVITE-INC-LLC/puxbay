package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.PaginatedResponse;
import com.puxbay.models.Staff;

public class StaffResource {
    private final Puxbay client;

    public StaffResource(Puxbay client) {
        this.client = client;
    }

    public PaginatedResponse<Staff> list(int page, String role) throws PuxbayException {
        String query = "staff/?page=" + page;
        if (role != null) query += "&role=" + role;
        return (PaginatedResponse<Staff>) client.request("GET", query, null, PaginatedResponse.class);
    }

    public Staff get(String staffId) throws PuxbayException {
        return client.request("GET", "staff/" + staffId + "/", null, Staff.class);
    }

    public Staff create(Staff staff) throws PuxbayException {
        return client.request("POST", "staff/", staff, Staff.class);
    }

    public Staff update(String staffId, Staff staff) throws PuxbayException {
        return client.request("PATCH", "staff/" + staffId + "/", staff, Staff.class);
    }

    public void delete(String staffId) throws PuxbayException {
        client.request("DELETE", "staff/" + staffId + "/", null, Void.class);
    }
}
