package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.PaginatedResponse;
import com.puxbay.models.Branch;

public class BranchesResource {
    private final Puxbay client;

    public BranchesResource(Puxbay client) {
        this.client = client;
    }

    public PaginatedResponse<Branch> list(int page) throws PuxbayException {
        return (PaginatedResponse<Branch>) client.request("GET", "branches/?page=" + page, null, PaginatedResponse.class);
    }

    public Branch get(String branchId) throws PuxbayException {
        return client.request("GET", "branches/" + branchId + "/", null, Branch.class);
    }

    public Branch create(Branch branch) throws PuxbayException {
        return client.request("POST", "branches/", branch, Branch.class);
    }

    public Branch update(String branchId, Branch branch) throws PuxbayException {
        return client.request("PATCH", "branches/" + branchId + "/", branch, Branch.class);
    }

    public void delete(String branchId) throws PuxbayException {
        client.request("DELETE", "branches/" + branchId + "/", null, Void.class);
    }
}
