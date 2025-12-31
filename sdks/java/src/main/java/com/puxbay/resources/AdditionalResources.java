package com.puxbay.resources;

import com.puxbay.Puxbay;
import com.puxbay.exceptions.PuxbayException;
import com.puxbay.models.*;
import com.google.gson.reflect.TypeToken;
import java.lang.reflect.Type;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Inventory resource - Inventory tracking operations.
 */
public class InventoryResource extends BaseResource {
    public InventoryResource(Puxbay client) {
        super(client);
    }
    
    public List<StockLevel> getStockLevels(String branchId) throws PuxbayException {
        Type type = new TypeToken<List<StockLevel>>(){}.getType();
        return client.request("GET", String.format("inventory/stock-levels/?branch=%s", branchId), null, type);
    }
    
    public StockLevel getProductStock(String productId, String branchId) throws PuxbayException {
        return get(String.format("inventory/product-stock/?product=%s&branch=%s", productId, branchId), StockLevel.class);
    }
}

/**
 * Reports resource - Sales reports and analytics.
 */
public class ReportsResource extends BaseResource {
    public ReportsResource(Puxbay client) {
        super(client);
    }
    
    public FinancialSummary getFinancialSummary(String startDate, String endDate) throws PuxbayException {
        return get(String.format("reports/financial-summary/?start_date=%s&end_date=%s", startDate, endDate), FinancialSummary.class);
    }
    
    public List<DailySales> getDailySales(String startDate, String endDate) throws PuxbayException {
        Type type = new TypeToken<List<DailySales>>(){}.getType();
        return client.request("GET", String.format("reports/daily-sales/?start_date=%s&end_date=%s", startDate, endDate), null, type);
    }
    
    public List<Product> getTopProducts(int limit) throws PuxbayException {
        Type type = new TypeToken<List<Product>>(){}.getType();
        return client.request("GET", String.format("reports/top-products/?limit=%d", limit), null, type);
    }
    
    public List<Product> getLowStock() throws PuxbayException {
        Type type = new TypeToken<List<Product>>(){}.getType();
        return client.request("GET", "reports/low-stock/", null, type);
    }
}

/**
 * Purchase Orders resource - Purchase order management.
 */
public class PurchaseOrdersResource extends BaseResource {
    public PurchaseOrdersResource(Puxbay client) {
        super(client);
    }
    
    public PaginatedResponse<PurchaseOrder> list(int page, String status) throws PuxbayException {
        String endpoint = String.format("purchase-orders/?page=%d", page);
        if (status != null && !status.isEmpty()) {
            endpoint += "&status=" + status;
        }
        Type type = new TypeToken<PaginatedResponse<PurchaseOrder>>(){}.getType();
        return client.request("GET", endpoint, null, type);
    }
    
    public PurchaseOrder get(String poId) throws PuxbayException {
        return get(String.format("purchase-orders/%s/", poId), PurchaseOrder.class);
    }
    
    public PurchaseOrder create(PurchaseOrder po) throws PuxbayException {
        return post("purchase-orders/", po, PurchaseOrder.class);
    }
    
    public PurchaseOrder update(String poId, PurchaseOrder po) throws PuxbayException {
        return patch(String.format("purchase-orders/%s/", poId), po, PurchaseOrder.class);
    }
    
    public PurchaseOrder receive(String poId, List<PurchaseOrderItem> items) throws PuxbayException {
        Map<String, Object> body = new HashMap<>();
        body.put("items", items);
        return post(String.format("purchase-orders/%s/receive/", poId), body, PurchaseOrder.class);
    }
}

/**
 * Stock Transfers resource - Stock transfer management.
 */
public class StockTransfersResource extends BaseResource {
    public StockTransfersResource(Puxbay client) {
        super(client);
    }
    
    public PaginatedResponse<StockTransfer> list(int page, String status) throws PuxbayException {
        String endpoint = String.format("stock-transfers/?page=%d", page);
        if (status != null && !status.isEmpty()) {
            endpoint += "&status=" + status;
        }
        Type type = new TypeToken<PaginatedResponse<StockTransfer>>(){}.getType();
        return client.request("GET", endpoint, null, type);
    }
    
    public StockTransfer get(String transferId) throws PuxbayException {
        return get(String.format("stock-transfers/%s/", transferId), StockTransfer.class);
    }
    
    public StockTransfer create(StockTransfer transfer) throws PuxbayException {
        return post("stock-transfers/", transfer, StockTransfer.class);
    }
    
    public StockTransfer complete(String transferId) throws PuxbayException {
        return post(String.format("stock-transfers/%s/complete/", transferId), null, StockTransfer.class);
    }
}

/**
 * Stocktakes resource - Stocktake session management.
 */
public class StocktakesResource extends BaseResource {
    public StocktakesResource(Puxbay client) {
        super(client);
    }
    
    public PaginatedResponse<StocktakeSession> list(int page) throws PuxbayException {
        Type type = new TypeToken<PaginatedResponse<StocktakeSession>>(){}.getType();
        return client.request("GET", String.format("stocktakes/?page=%d", page), null, type);
    }
    
    public StocktakeSession get(String stocktakeId) throws PuxbayException {
        return get(String.format("stocktakes/%s/", stocktakeId), StocktakeSession.class);
    }
    
    public StocktakeSession create(StocktakeSession stocktake) throws PuxbayException {
        return post("stocktakes/", stocktake, StocktakeSession.class);
    }
    
    public StocktakeSession complete(String stocktakeId) throws PuxbayException {
        return post(String.format("stocktakes/%s/complete/", stocktakeId), null, StocktakeSession.class);
    }
}

/**
 * Cash Drawers resource - Cash drawer session management.
 */
public class CashDrawersResource extends BaseResource {
    public CashDrawersResource(Puxbay client) {
        super(client);
    }
    
    public PaginatedResponse<CashDrawerSession> list(int page) throws PuxbayException {
        Type type = new TypeToken<PaginatedResponse<CashDrawerSession>>(){}.getType();
        return client.request("GET", String.format("cash-drawers/?page=%d", page), null, type);
    }
    
    public CashDrawerSession get(String drawerId) throws PuxbayException {
        return get(String.format("cash-drawers/%s/", drawerId), CashDrawerSession.class);
    }
    
    public CashDrawerSession open(CashDrawerSession drawer) throws PuxbayException {
        return post("cash-drawers/", drawer, CashDrawerSession.class);
    }
    
    public CashDrawerSession close(String drawerId, double actualCash) throws PuxbayException {
        Map<String, Object> body = new HashMap<>();
        body.put("actual_cash", actualCash);
        return post(String.format("cash-drawers/%s/close/", drawerId), body, CashDrawerSession.class);
    }
}

/**
 * Expenses resource - Expense tracking operations.
 */
public class ExpensesResource extends BaseResource {
    public ExpensesResource(Puxbay client) {
        super(client);
    }
    
    public PaginatedResponse<Expense> list(int page, String category) throws PuxbayException {
        String endpoint = String.format("expenses/?page=%d", page);
        if (category != null && !category.isEmpty()) {
            endpoint += "&category=" + category;
        }
        Type type = new TypeToken<PaginatedResponse<Expense>>(){}.getType();
        return client.request("GET", endpoint, null, type);
    }
    
    public Expense get(String expenseId) throws PuxbayException {
        return get(String.format("expenses/%s/", expenseId), Expense.class);
    }
    
    public Expense create(Expense expense) throws PuxbayException {
        return post("expenses/", expense, Expense.class);
    }
    
    public Expense update(String expenseId, Expense expense) throws PuxbayException {
        return patch(String.format("expenses/%s/", expenseId), expense, Expense.class);
    }
    
    public void delete(String expenseId) throws PuxbayException {
        delete(String.format("expenses/%s/", expenseId));
    }
    
    public List<ExpenseCategory> listCategories() throws PuxbayException {
        Type type = new TypeToken<List<ExpenseCategory>>(){}.getType();
        return client.request("GET", "expense-categories/", null, type);
    }
}

/**
 * Notifications resource - Notification management.
 */
public class NotificationsResource extends BaseResource {
    public NotificationsResource(Puxbay client) {
        super(client);
    }
    
    public PaginatedResponse<Notification> list(int page) throws PuxbayException {
        Type type = new TypeToken<PaginatedResponse<Notification>>(){}.getType();
        return client.request("GET", String.format("notifications/?page=%d", page), null, type);
    }
    
    public Notification get(String notificationId) throws PuxbayException {
        return get(String.format("notifications/%s/", notificationId), Notification.class);
    }
    
    public Notification markAsRead(String notificationId) throws PuxbayException {
        return post(String.format("notifications/%s/mark-read/", notificationId), null, Notification.class);
    }
}

/**
 * Returns resource - Return processing operations.
 */
public class ReturnsResource extends BaseResource {
    public ReturnsResource(Puxbay client) {
        super(client);
    }
    
    public PaginatedResponse<Return> list(int page) throws PuxbayException {
        Type type = new TypeToken<PaginatedResponse<Return>>(){}.getType();
        return client.request("GET", String.format("returns/?page=%d", page), null, type);
    }
    
    public Return get(String returnId) throws PuxbayException {
        return get(String.format("returns/%s/", returnId), Return.class);
    }
    
    public Return create(Return returnObj) throws PuxbayException {
        return post("returns/", returnObj, Return.class);
    }
    
    public Return approve(String returnId) throws PuxbayException {
        return post(String.format("returns/%s/approve/", returnId), null, Return.class);
    }
}
