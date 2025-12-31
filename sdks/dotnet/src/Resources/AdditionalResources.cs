using System.Collections.Generic;
using System.Net.Http;
using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    /// <summary>
    /// Inventory resource - Inventory tracking operations.
    /// </summary>
    public class InventoryResource : BaseResource
    {
        public InventoryResource(PuxbayClient client) : base(client) { }
        
        public async Task<List<StockLevel>> GetStockLevelsAsync(string branchId)
        {
            return await Client.RequestAsync<List<StockLevel>>(
                HttpMethod.Get, 
                $"inventory/stock-levels/?branch={branchId}"
            );
        }
        
        public async Task<StockLevel> GetProductStockAsync(string productId, string branchId)
        {
            return await Client.RequestAsync<StockLevel>(
                HttpMethod.Get, 
                $"inventory/product-stock/?product={productId}&branch={branchId}"
            );
        }
    }
    
    /// <summary>
    /// Reports resource - Sales reports and analytics.
    /// </summary>
    public class ReportsResource : BaseResource
    {
        public ReportsResource(PuxbayClient client) : base(client) { }
        
        public async Task<FinancialSummary> GetFinancialSummaryAsync(string startDate, string endDate)
        {
            return await Client.RequestAsync<FinancialSummary>(
                HttpMethod.Get, 
                $"reports/financial-summary/?start_date={startDate}&end_date={endDate}"
            );
        }
        
        public async Task<List<DailySales>> GetDailySalesAsync(string startDate, string endDate)
        {
            return await Client.RequestAsync<List<DailySales>>(
                HttpMethod.Get, 
                $"reports/daily-sales/?start_date={startDate}&end_date={endDate}"
            );
        }
        
        public async Task<List<Product>> GetTopProductsAsync(int limit = 10)
        {
            return await Client.RequestAsync<List<Product>>(
                HttpMethod.Get, 
                $"reports/top-products/?limit={limit}"
            );
        }
        
        public async Task<List<Product>> GetLowStockAsync()
        {
            return await Client.RequestAsync<List<Product>>(HttpMethod.Get, "reports/low-stock/");
        }
    }
    
    /// <summary>
    /// Purchase Orders resource - Purchase order management.
    /// </summary>
    public class PurchaseOrdersResource : BaseResource
    {
        public PurchaseOrdersResource(PuxbayClient client) : base(client) { }
        
        public async Task<PaginatedResponse<PurchaseOrder>> ListAsync(int page = 1, string status = null)
        {
            var endpoint = $"purchase-orders/?page={page}";
            if (!string.IsNullOrEmpty(status))
            {
                endpoint += $"&status={status}";
            }
            return await Client.RequestAsync<PaginatedResponse<PurchaseOrder>>(HttpMethod.Get, endpoint);
        }
        
        public async Task<PurchaseOrder> GetAsync(string poId)
        {
            return await Client.RequestAsync<PurchaseOrder>(HttpMethod.Get, $"purchase-orders/{poId}/");
        }
        
        public async Task<PurchaseOrder> CreateAsync(PurchaseOrder po)
        {
            return await Client.RequestAsync<PurchaseOrder>(HttpMethod.Post, "purchase-orders/", po);
        }
        
        public async Task<PurchaseOrder> UpdateAsync(string poId, PurchaseOrder po)
        {
            return await Client.RequestAsync<PurchaseOrder>(HttpMethod.Patch, $"purchase-orders/{poId}/", po);
        }
        
        public async Task<PurchaseOrder> ReceiveAsync(string poId, List<PurchaseOrderItem> items)
        {
            var body = new { items };
            return await Client.RequestAsync<PurchaseOrder>(HttpMethod.Post, $"purchase-orders/{poId}/receive/", body);
        }
    }
    
    /// <summary>
    /// Stock Transfers resource - Stock transfer management.
    /// </summary>
    public class StockTransfersResource : BaseResource
    {
        public StockTransfersResource(PuxbayClient client) : base(client) { }
        
        public async Task<PaginatedResponse<StockTransfer>> ListAsync(int page = 1, string status = null)
        {
            var endpoint = $"stock-transfers/?page={page}";
            if (!string.IsNullOrEmpty(status))
            {
                endpoint += $"&status={status}";
            }
            return await Client.RequestAsync<PaginatedResponse<StockTransfer>>(HttpMethod.Get, endpoint);
        }
        
        public async Task<StockTransfer> GetAsync(string transferId)
        {
            return await Client.RequestAsync<StockTransfer>(HttpMethod.Get, $"stock-transfers/{transferId}/");
        }
        
        public async Task<StockTransfer> CreateAsync(StockTransfer transfer)
        {
            return await Client.RequestAsync<StockTransfer>(HttpMethod.Post, "stock-transfers/", transfer);
        }
        
        public async Task<StockTransfer> CompleteAsync(string transferId)
        {
            return await Client.RequestAsync<StockTransfer>(HttpMethod.Post, $"stock-transfers/{transferId}/complete/");
        }
    }
    
    /// <summary>
    /// Stocktakes resource - Stocktake session management.
    /// </summary>
    public class StocktakesResource : BaseResource
    {
        public StocktakesResource(PuxbayClient client) : base(client) { }
        
        public async Task<PaginatedResponse<StocktakeSession>> ListAsync(int page = 1)
        {
            return await Client.RequestAsync<PaginatedResponse<StocktakeSession>>(
                HttpMethod.Get, 
                $"stocktakes/?page={page}"
            );
        }
        
        public async Task<StocktakeSession> GetAsync(string stocktakeId)
        {
            return await Client.RequestAsync<StocktakeSession>(HttpMethod.Get, $"stocktakes/{stocktakeId}/");
        }
        
        public async Task<StocktakeSession> CreateAsync(StocktakeSession stocktake)
        {
            return await Client.RequestAsync<StocktakeSession>(HttpMethod.Post, "stocktakes/", stocktake);
        }
        
        public async Task<StocktakeSession> CompleteAsync(string stocktakeId)
        {
            return await Client.RequestAsync<StocktakeSession>(HttpMethod.Post, $"stocktakes/{stocktakeId}/complete/");
        }
    }
    
    /// <summary>
    /// Cash Drawers resource - Cash drawer session management.
    /// </summary>
    public class CashDrawersResource : BaseResource
    {
        public CashDrawersResource(PuxbayClient client) : base(client) { }
        
        public async Task<PaginatedResponse<CashDrawerSession>> ListAsync(int page = 1)
        {
            return await Client.RequestAsync<PaginatedResponse<CashDrawerSession>>(
                HttpMethod.Get, 
                $"cash-drawers/?page={page}"
            );
        }
        
        public async Task<CashDrawerSession> GetAsync(string drawerId)
        {
            return await Client.RequestAsync<CashDrawerSession>(HttpMethod.Get, $"cash-drawers/{drawerId}/");
        }
        
        public async Task<CashDrawerSession> OpenAsync(CashDrawerSession drawer)
        {
            return await Client.RequestAsync<CashDrawerSession>(HttpMethod.Post, "cash-drawers/", drawer);
        }
        
        public async Task<CashDrawerSession> CloseAsync(string drawerId, decimal actualCash)
        {
            var body = new { actual_cash = actualCash };
            return await Client.RequestAsync<CashDrawerSession>(HttpMethod.Post, $"cash-drawers/{drawerId}/close/", body);
        }
    }
    
    /// <summary>
    /// Expenses resource - Expense tracking operations.
    /// </summary>
    public class ExpensesResource : BaseResource
    {
        public ExpensesResource(PuxbayClient client) : base(client) { }
        
        public async Task<PaginatedResponse<Expense>> ListAsync(int page = 1, string category = null)
        {
            var endpoint = $"expenses/?page={page}";
            if (!string.IsNullOrEmpty(category))
            {
                endpoint += $"&category={category}";
            }
            return await Client.RequestAsync<PaginatedResponse<Expense>>(HttpMethod.Get, endpoint);
        }
        
        public async Task<Expense> GetAsync(string expenseId)
        {
            return await Client.RequestAsync<Expense>(HttpMethod.Get, $"expenses/{expenseId}/");
        }
        
        public async Task<Expense> CreateAsync(Expense expense)
        {
            return await Client.RequestAsync<Expense>(HttpMethod.Post, "expenses/", expense);
        }
        
        public async Task<Expense> UpdateAsync(string expenseId, Expense expense)
        {
            return await Client.RequestAsync<Expense>(HttpMethod.Patch, $"expenses/{expenseId}/", expense);
        }
        
        public async Task DeleteAsync(string expenseId)
        {
            await Client.RequestAsync<object>(HttpMethod.Delete, $"expenses/{expenseId}/");
        }
        
        public async Task<List<ExpenseCategory>> ListCategoriesAsync()
        {
            return await Client.RequestAsync<List<ExpenseCategory>>(HttpMethod.Get, "expense-categories/");
        }
    }
    
    /// <summary>
    /// Notifications resource - Notification management.
    /// </summary>
    public class NotificationsResource : BaseResource
    {
        public NotificationsResource(PuxbayClient client) : base(client) { }
        
        public async Task<PaginatedResponse<Notification>> ListAsync(int page = 1)
        {
            return await Client.RequestAsync<PaginatedResponse<Notification>>(
                HttpMethod.Get, 
                $"notifications/?page={page}"
            );
        }
        
        public async Task<Notification> GetAsync(string notificationId)
        {
            return await Client.RequestAsync<Notification>(HttpMethod.Get, $"notifications/{notificationId}/");
        }
        
        public async Task<Notification> MarkAsReadAsync(string notificationId)
        {
            return await Client.RequestAsync<Notification>(HttpMethod.Post, $"notifications/{notificationId}/mark-read/");
        }
    }
    
    /// <summary>
    /// Returns resource - Return processing operations.
    /// </summary>
    public class ReturnsResource : BaseResource
    {
        public ReturnsResource(PuxbayClient client) : base(client) { }
        
        public async Task<PaginatedResponse<Return>> ListAsync(int page = 1)
        {
            return await Client.RequestAsync<PaginatedResponse<Return>>(HttpMethod.Get, $"returns/?page={page}");
        }
        
        public async Task<Return> GetAsync(string returnId)
        {
            return await Client.RequestAsync<Return>(HttpMethod.Get, $"returns/{returnId}/");
        }
        
        public async Task<Return> CreateAsync(Return returnObj)
        {
            return await Client.RequestAsync<Return>(HttpMethod.Post, "returns/", returnObj);
        }
        
        public async Task<Return> ApproveAsync(string returnId)
        {
            return await Client.RequestAsync<Return>(HttpMethod.Post, $"returns/{returnId}/approve/");
        }
    }
}
