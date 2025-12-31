package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.*;
import com.google.gson.reflect.TypeToken;
import java.lang.reflect.Type;
import java.util.HashMap;
import java.util.Map;

/**
 * Base resource class with common HTTP methods.
 */
public abstract class BaseResource {
    protected final Puxbay client;
    
    protected BaseResource(Puxbay client) {
        this.client = client;
    }
    
    protected <T> T get(String endpoint, Class<T> responseType) throws PuxbayException {
        return client.request("GET", endpoint, null, responseType);
    }
    
    protected <T> T post(String endpoint, Object body, Class<T> responseType) throws PuxbayException {
        return client.request("POST", endpoint, body, responseType);
    }
    
    protected <T> T patch(String endpoint, Object body, Class<T> responseType) throws PuxbayException {
        return client.request("PATCH", endpoint, body, responseType);
    }
    
    protected void delete(String endpoint) throws PuxbayException {
        client.request("DELETE", endpoint, null, Void.class);
    }
}

/**
 * Products resource - Product management operations.
 */
public class ProductsResource extends BaseResource {
    public ProductsResource(Puxbay client) {
        super(client);
    }
    
    public PaginatedResponse<Product> list(int page, int pageSize) throws PuxbayException {
        Type type = new TypeToken<PaginatedResponse<Product>>(){}.getType();
        return client.request("GET", String.format("products/?page=%d&page_size=%d", page, pageSize), null, type);
    }
    
    public Product get(String productId) throws PuxbayException {
        return get(String.format("products/%s/", productId), Product.class);
    }
    
    public Product create(Product product) throws PuxbayException {
        return post("products/", product, Product.class);
    }
    
    public Product update(String productId, Product product) throws PuxbayException {
        return patch(String.format("products/%s/", productId), product, Product.class);
    }
    
    public void delete(String productId) throws PuxbayException {
        delete(String.format("products/%s/", productId));
    }
    
    public Product adjustStock(String productId, int quantity, String reason) throws PuxbayException {
        Map<String, Object> body = new HashMap<>();
        body.put("quantity", quantity);
        body.put("reason", reason);
        return post(String.format("products/%s/stock-adjustment/", productId), body, Product.class);
    }
    
    public PaginatedResponse<ProductHistory> history(String productId, int page) throws PuxbayException {
        Type type = new TypeToken<PaginatedResponse<ProductHistory>>(){}.getType();
        return client.request("GET", String.format("products/%s/history/?page=%d", productId, page), null, type);
    }
}

/**
 * Orders resource - Order management operations.
 */
public class OrdersResource extends BaseResource {
    public OrdersResource(Puxbay client) {
        super(client);
    }
    
    public PaginatedResponse<Order> list(int page, int pageSize) throws PuxbayException {
        Type type = new TypeToken<PaginatedResponse<Order>>(){}.getType();
        return client.request("GET", String.format("orders/?page=%d&page_size=%d", page, pageSize), null, type);
    }
    
    public Order get(String orderId) throws PuxbayException {
        return get(String.format("orders/%s/", orderId), Order.class);
    }
    
    public Order create(Order order) throws PuxbayException {
        return post("orders/", order, Order.class);
    }
    
    public Order cancel(String orderId) throws PuxbayException {
        return post(String.format("orders/%s/cancel/", orderId), null, Order.class);
    }
}

/**
 * Customers resource - Customer management operations.
 */
public class CustomersResource extends BaseResource {
    public CustomersResource(Puxbay client) {
        super(client);
    }
    
    public PaginatedResponse<Customer> list(int page, int pageSize) throws PuxbayException {
        Type type = new TypeToken<PaginatedResponse<Customer>>(){}.getType();
        return client.request("GET", String.format("customers/?page=%d&page_size=%d", page, pageSize), null, type);
    }
    
    public Customer get(String customerId) throws PuxbayException {
        return get(String.format("customers/%s/", customerId), Customer.class);
    }
    
    public Customer create(Customer customer) throws PuxbayException {
        return post("customers/", customer, Customer.class);
    }
    
    public Customer update(String customerId, Customer customer) throws PuxbayException {
        return patch(String.format("customers/%s/", customerId), customer, Customer.class);
    }
    
    public void delete(String customerId) throws PuxbayException {
        delete(String.format("customers/%s/", customerId));
    }
    
    public Customer adjustLoyaltyPoints(String customerId, int points, String description) throws PuxbayException {
        Map<String, Object> body = new HashMap<>();
        body.put("points", points);
        body.put("description", description);
        return post(String.format("customers/%s/adjust-loyalty-points/", customerId), body, Customer.class);
    }
    
    public Customer adjustStoreCredit(String customerId, double amount, String reference) throws PuxbayException {
        Map<String, Object> body = new HashMap<>();
        body.put("amount", amount);
        body.put("reference", reference);
        return post(String.format("customers/%s/adjust-store-credit/", customerId), body, Customer.class);
    }
}

/**
 * Categories resource - Category management operations.
 */
public class CategoriesResource extends BaseResource {
    public CategoriesResource(Puxbay client) {
        super(client);
    }
    
    public PaginatedResponse<Category> list(int page) throws PuxbayException {
        Type type = new TypeToken<PaginatedResponse<Category>>(){}.getType();
        return client.request("GET", String.format("categories/?page=%d", page), null, type);
    }
    
    public Category get(String categoryId) throws PuxbayException {
        return get(String.format("categories/%s/", categoryId), Category.class);
    }
    
    public Category create(Category category) throws PuxbayException {
        return post("categories/", category, Category.class);
    }
    
    public Category update(String categoryId, Category category) throws PuxbayException {
        return patch(String.format("categories/%s/", categoryId), category, Category.class);
    }
    
    public void delete(String categoryId) throws PuxbayException {
        delete(String.format("categories/%s/", categoryId));
    }
}

/**
 * Suppliers resource - Supplier management operations.
 */
public class SuppliersResource extends BaseResource {
    public SuppliersResource(Puxbay client) {
        super(client);
    }
    
    public PaginatedResponse<Supplier> list(int page, int pageSize) throws PuxbayException {
        Type type = new TypeToken<PaginatedResponse<Supplier>>(){}.getType();
        return client.request("GET", String.format("suppliers/?page=%d&page_size=%d", page, pageSize), null, type);
    }
    
    public Supplier get(String supplierId) throws PuxbayException {
        return get(String.format("suppliers/%s/", supplierId), Supplier.class);
    }
    
    public Supplier create(Supplier supplier) throws PuxbayException {
        return post("suppliers/", supplier, Supplier.class);
    }
    
    public Supplier update(String supplierId, Supplier supplier) throws PuxbayException {
        return patch(String.format("suppliers/%s/", supplierId), supplier, Supplier.class);
    }
    
    public void delete(String supplierId) throws PuxbayException {
        delete(String.format("suppliers/%s/", supplierId));
    }
}

/**
 * Gift Cards resource - Gift card operations.
 */
public class GiftCardsResource extends BaseResource {
    public GiftCardsResource(Puxbay client) {
        super(client);
    }
    
    public PaginatedResponse<GiftCard> list(int page, String status) throws PuxbayException {
        String endpoint = String.format("gift-cards/?page=%d", page);
        if (status != null && !status.isEmpty()) {
            endpoint += "&status=" + status;
        }
        Type type = new TypeToken<PaginatedResponse<GiftCard>>(){}.getType();
        return client.request("GET", endpoint, null, type);
    }
    
    public GiftCard get(String cardId) throws PuxbayException {
        return get(String.format("gift-cards/%s/", cardId), GiftCard.class);
    }
    
    public GiftCard create(GiftCard card) throws PuxbayException {
        return post("gift-cards/", card, GiftCard.class);
    }
    
    public GiftCard redeem(String cardId, double amount) throws PuxbayException {
        Map<String, Object> body = new HashMap<>();
        body.put("amount", amount);
        return post(String.format("gift-cards/%s/redeem/", cardId), body, GiftCard.class);
    }
    
    public GiftCard checkBalance(String code) throws PuxbayException {
        return get(String.format("gift-cards/check-balance/?code=%s", code), GiftCard.class);
    }
}

/**
 * Branches resource - Branch management operations.
 */
public class BranchesResource extends BaseResource {
    public BranchesResource(Puxbay client) {
        super(client);
    }
    
    public PaginatedResponse<Branch> list(int page) throws PuxbayException {
        Type type = new TypeToken<PaginatedResponse<Branch>>(){}.getType();
        return client.request("GET", String.format("branches/?page=%d", page), null, type);
    }
    
    public Branch get(String branchId) throws PuxbayException {
        return get(String.format("branches/%s/", branchId), Branch.class);
    }
    
    public Branch create(Branch branch) throws PuxbayException {
        return post("branches/", branch, Branch.class);
    }
    
    public Branch update(String branchId, Branch branch) throws PuxbayException {
        return patch(String.format("branches/%s/", branchId), branch, Branch.class);
    }
    
    public void delete(String branchId) throws PuxbayException {
        delete(String.format("branches/%s/", branchId));
    }
}

/**
 * Staff resource - Staff management operations.
 */
public class StaffResource extends BaseResource {
    public StaffResource(Puxbay client) {
        super(client);
    }
    
    public PaginatedResponse<Staff> list(int page, String role) throws PuxbayException {
        String endpoint = String.format("staff/?page=%d", page);
        if (role != null && !role.isEmpty()) {
            endpoint += "&role=" + role;
        }
        Type type = new TypeToken<PaginatedResponse<Staff>>(){}.getType();
        return client.request("GET", endpoint, null, type);
    }
    
    public Staff get(String staffId) throws PuxbayException {
        return get(String.format("staff/%s/", staffId), Staff.class);
    }
    
    public Staff create(Staff staff) throws PuxbayException {
        return post("staff/", staff, Staff.class);
    }
    
    public Staff update(String staffId, Staff staff) throws PuxbayException {
        return patch(String.format("staff/%s/", staffId), staff, Staff.class);
    }
    
    public void delete(String staffId) throws PuxbayException {
        delete(String.format("staff/%s/", staffId));
    }
}

/**
 * Webhooks resource - Webhook configuration operations.
 */
public class WebhooksResource extends BaseResource {
    public WebhooksResource(Puxbay client) {
        super(client);
    }
    
    public PaginatedResponse<Webhook> list(int page) throws PuxbayException {
        Type type = new TypeToken<PaginatedResponse<Webhook>>(){}.getType();
        return client.request("GET", String.format("webhooks/?page=%d", page), null, type);
    }
    
    public Webhook get(String webhookId) throws PuxbayException {
        return get(String.format("webhooks/%s/", webhookId), Webhook.class);
    }
    
    public Webhook create(Webhook webhook) throws PuxbayException {
        return post("webhooks/", webhook, Webhook.class);
    }
    
    public Webhook update(String webhookId, Webhook webhook) throws PuxbayException {
        return patch(String.format("webhooks/%s/", webhookId), webhook, Webhook.class);
    }
    
    public void delete(String webhookId) throws PuxbayException {
        delete(String.format("webhooks/%s/", webhookId));
    }
    
    public PaginatedResponse<WebhookEvent> listEvents(String webhookId, int page) throws PuxbayException {
        Type type = new TypeToken<PaginatedResponse<WebhookEvent>>(){}.getType();
        return client.request("GET", String.format("webhook-logs/?webhook=%s&page=%d", webhookId, page), null, type);
    }
}

// Placeholder classes for remaining resources following same pattern
public class InventoryResource extends BaseResource {
    public InventoryResource(Puxbay client) { super(client); }
}

public class ReportsResource extends BaseResource {
    public ReportsResource(Puxbay client) { super(client); }
}

public class PurchaseOrdersResource extends BaseResource {
    public PurchaseOrdersResource(Puxbay client) { super(client); }
}

public class StockTransfersResource extends BaseResource {
    public StockTransfersResource(Puxbay client) { super(client); }
}

public class StocktakesResource extends BaseResource {
    public StocktakesResource(Puxbay client) { super(client); }
}

public class CashDrawersResource extends BaseResource {
    public CashDrawersResource(Puxbay client) { super(client); }
}

public class ExpensesResource extends BaseResource {
    public ExpensesResource(Puxbay client) { super(client); }
}

public class NotificationsResource extends BaseResource {
    public NotificationsResource(Puxbay client) { super(client); }
}

public class ReturnsResource extends BaseResource {
    public ReturnsResource(Puxbay client) { super(client); }
}
