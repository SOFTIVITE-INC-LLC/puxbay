package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.PaginatedResponse;
import com.puxbay.models.Expense;
import java.util.List;

public class ExpensesResource {
    private final Puxbay client;

    public ExpensesResource(Puxbay client) {
        this.client = client;
    }

    public PaginatedResponse<Expense> list(int page, String category) throws PuxbayException {
        String query = "expenses/?page=" + page;
        if (category != null) query += "&category=" + category;
        return (PaginatedResponse<Expense>) client.request("GET", query, null, PaginatedResponse.class);
    }

    public Expense get(String expenseId) throws PuxbayException {
        return client.request("GET", "expenses/" + expenseId + "/", null, Expense.class);
    }

    public Expense create(Expense expense) throws PuxbayException {
        return client.request("POST", "expenses/", expense, Expense.class);
    }

    public Expense update(String expenseId, Expense expense) throws PuxbayException {
        return client.request("PATCH", "expenses/" + expenseId + "/", expense, Expense.class);
    }

    public void delete(String expenseId) throws PuxbayException {
        client.request("DELETE", "expenses/" + expenseId + "/", null, Void.class);
    }
    
    public List<String> listCategories() throws PuxbayException {
        return client.request("GET", "expense-categories/", null, List.class);
    }
}
