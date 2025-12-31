using System.Net.Http;
using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    /// <summary>
    /// Base resource class with common HTTP methods.
    /// </summary>
    public abstract class BaseResource
    {
        protected readonly PuxbayClient Client;
        
        protected BaseResource(PuxbayClient client)
        {
            Client = client;
        }
    }
    
    /// <summary>
    /// Products resource - Product management operations.
    /// </summary>
    public class ProductsResource : BaseResource
    {
        public ProductsResource(PuxbayClient client) : base(client) { }
        
        public async Task<PaginatedResponse<Product>> ListAsync(int page = 1, int pageSize = 20)
        {
            return await Client.RequestAsync<PaginatedResponse<Product>>(
                HttpMethod.Get, 
                $"products/?page={page}&page_size={pageSize}"
            );
        }
        
        public async Task<Product> GetAsync(string productId)
        {
            return await Client.RequestAsync<Product>(HttpMethod.Get, $"products/{productId}/");
        }
        
        public async Task<Product> CreateAsync(Product product)
        {
            return await Client.RequestAsync<Product>(HttpMethod.Post, "products/", product);
        }
        
        public async Task<Product> UpdateAsync(string productId, Product product)
        {
            return await Client.RequestAsync<Product>(HttpMethod.Patch, $"products/{productId}/", product);
        }
        
        public async Task DeleteAsync(string productId)
        {
            await Client.RequestAsync<object>(HttpMethod.Delete, $"products/{productId}/");
        }
        
        public async Task<Product> AdjustStockAsync(string productId, int quantity, string reason)
        {
            var body = new { quantity, reason };
            return await Client.RequestAsync<Product>(HttpMethod.Post, $"products/{productId}/stock-adjustment/", body);
        }
        
        public async Task<PaginatedResponse<ProductHistory>> HistoryAsync(string productId, int page = 1)
        {
            return await Client.RequestAsync<PaginatedResponse<ProductHistory>>(
                HttpMethod.Get, 
                $"products/{productId}/history/?page={page}"
            );
        }
    }
    
    /// <summary>
    /// Orders resource - Order management operations.
    /// </summary>
    public class OrdersResource : BaseResource
    {
        public OrdersResource(PuxbayClient client) : base(client) { }
        
        public async Task<PaginatedResponse<Order>> ListAsync(int page = 1, int pageSize = 20)
        {
            return await Client.RequestAsync<PaginatedResponse<Order>>(
                HttpMethod.Get, 
                $"orders/?page={page}&page_size={pageSize}"
            );
        }
        
        public async Task<Order> GetAsync(string orderId)
        {
            return await Client.RequestAsync<Order>(HttpMethod.Get, $"orders/{orderId}/");
        }
        
        public async Task<Order> CreateAsync(Order order)
        {
            return await Client.RequestAsync<Order>(HttpMethod.Post, "orders/", order);
        }
        
        public async Task<Order> CancelAsync(string orderId)
        {
            return await Client.RequestAsync<Order>(HttpMethod.Post, $"orders/{orderId}/cancel/");
        }
    }
    
    /// <summary>
    /// Customers resource - Customer management operations.
    /// </summary>
    public class CustomersResource : BaseResource
    {
        public CustomersResource(PuxbayClient client) : base(client) { }
        
        public async Task<PaginatedResponse<Customer>> ListAsync(int page = 1, int pageSize = 20)
        {
            return await Client.RequestAsync<PaginatedResponse<Customer>>(
                HttpMethod.Get, 
                $"customers/?page={page}&page_size={pageSize}"
            );
        }
        
        public async Task<Customer> GetAsync(string customerId)
        {
            return await Client.RequestAsync<Customer>(HttpMethod.Get, $"customers/{customerId}/");
        }
        
        public async Task<Customer> CreateAsync(Customer customer)
        {
            return await Client.RequestAsync<Customer>(HttpMethod.Post, "customers/", customer);
        }
        
        public async Task<Customer> UpdateAsync(string customerId, Customer customer)
        {
            return await Client.RequestAsync<Customer>(HttpMethod.Patch, $"customers/{customerId}/", customer);
        }
        
        public async Task DeleteAsync(string customerId)
        {
            await Client.RequestAsync<object>(HttpMethod.Delete, $"customers/{customerId}/");
        }
        
        public async Task<Customer> AdjustLoyaltyPointsAsync(string customerId, int points, string description)
        {
            var body = new { points, description };
            return await Client.RequestAsync<Customer>(HttpMethod.Post, $"customers/{customerId}/adjust-loyalty-points/", body);
        }
        
        public async Task<Customer> AdjustStoreCreditAsync(string customerId, decimal amount, string reference)
        {
            var body = new { amount, reference };
            return await Client.RequestAsync<Customer>(HttpMethod.Post, $"customers/{customerId}/adjust-store-credit/", body);
        }
    }
    
    /// <summary>
    /// Categories resource - Category management operations.
    /// </summary>
    public class CategoriesResource : BaseResource
    {
        public CategoriesResource(PuxbayClient client) : base(client) { }
        
        public async Task<PaginatedResponse<Category>> ListAsync(int page = 1)
        {
            return await Client.RequestAsync<PaginatedResponse<Category>>(HttpMethod.Get, $"categories/?page={page}");
        }
        
        public async Task<Category> GetAsync(string categoryId)
        {
            return await Client.RequestAsync<Category>(HttpMethod.Get, $"categories/{categoryId}/");
        }
        
        public async Task<Category> CreateAsync(Category category)
        {
            return await Client.RequestAsync<Category>(HttpMethod.Post, "categories/", category);
        }
        
        public async Task<Category> UpdateAsync(string categoryId, Category category)
        {
            return await Client.RequestAsync<Category>(HttpMethod.Patch, $"categories/{categoryId}/", category);
        }
        
        public async Task DeleteAsync(string categoryId)
        {
            await Client.RequestAsync<object>(HttpMethod.Delete, $"categories/{categoryId}/");
        }
    }
    
    /// <summary>
    /// Suppliers resource - Supplier management operations.
    /// </summary>
    public class SuppliersResource : BaseResource
    {
        public SuppliersResource(PuxbayClient client) : base(client) { }
        
        public async Task<PaginatedResponse<Supplier>> ListAsync(int page = 1, int pageSize = 20)
        {
            return await Client.RequestAsync<PaginatedResponse<Supplier>>(
                HttpMethod.Get, 
                $"suppliers/?page={page}&page_size={pageSize}"
            );
        }
        
        public async Task<Supplier> GetAsync(string supplierId)
        {
            return await Client.RequestAsync<Supplier>(HttpMethod.Get, $"suppliers/{supplierId}/");
        }
        
        public async Task<Supplier> CreateAsync(Supplier supplier)
        {
            return await Client.RequestAsync<Supplier>(HttpMethod.Post, "suppliers/", supplier);
        }
        
        public async Task<Supplier> UpdateAsync(string supplierId, Supplier supplier)
        {
            return await Client.RequestAsync<Supplier>(HttpMethod.Patch, $"suppliers/{supplierId}/", supplier);
        }
        
        public async Task DeleteAsync(string supplierId)
        {
            await Client.RequestAsync<object>(HttpMethod.Delete, $"suppliers/{supplierId}/");
        }
    }
    
    /// <summary>
    /// Gift Cards resource - Gift card operations.
    /// </summary>
    public class GiftCardsResource : BaseResource
    {
        public GiftCardsResource(PuxbayClient client) : base(client) { }
        
        public async Task<PaginatedResponse<GiftCard>> ListAsync(int page = 1, string status = null)
        {
            var endpoint = $"gift-cards/?page={page}";
            if (!string.IsNullOrEmpty(status))
            {
                endpoint += $"&status={status}";
            }
            return await Client.RequestAsync<PaginatedResponse<GiftCard>>(HttpMethod.Get, endpoint);
        }
        
        public async Task<GiftCard> GetAsync(string cardId)
        {
            return await Client.RequestAsync<GiftCard>(HttpMethod.Get, $"gift-cards/{cardId}/");
        }
        
        public async Task<GiftCard> CreateAsync(GiftCard card)
        {
            return await Client.RequestAsync<GiftCard>(HttpMethod.Post, "gift-cards/", card);
        }
        
        public async Task<GiftCard> RedeemAsync(string cardId, decimal amount)
        {
            var body = new { amount };
            return await Client.RequestAsync<GiftCard>(HttpMethod.Post, $"gift-cards/{cardId}/redeem/", body);
        }
        
        public async Task<GiftCard> CheckBalanceAsync(string code)
        {
            return await Client.RequestAsync<GiftCard>(HttpMethod.Get, $"gift-cards/check-balance/?code={code}");
        }
    }
    
    /// <summary>
    /// Branches resource - Branch management operations.
    /// </summary>
    public class BranchesResource : BaseResource
    {
        public BranchesResource(PuxbayClient client) : base(client) { }
        
        public async Task<PaginatedResponse<Branch>> ListAsync(int page = 1)
        {
            return await Client.RequestAsync<PaginatedResponse<Branch>>(HttpMethod.Get, $"branches/?page={page}");
        }
        
        public async Task<Branch> GetAsync(string branchId)
        {
            return await Client.RequestAsync<Branch>(HttpMethod.Get, $"branches/{branchId}/");
        }
        
        public async Task<Branch> CreateAsync(Branch branch)
        {
            return await Client.RequestAsync<Branch>(HttpMethod.Post, "branches/", branch);
        }
        
        public async Task<Branch> UpdateAsync(string branchId, Branch branch)
        {
            return await Client.RequestAsync<Branch>(HttpMethod.Patch, $"branches/{branchId}/", branch);
        }
        
        public async Task DeleteAsync(string branchId)
        {
            await Client.RequestAsync<object>(HttpMethod.Delete, $"branches/{branchId}/");
        }
    }
    
    /// <summary>
    /// Staff resource - Staff management operations.
    /// </summary>
    public class StaffResource : BaseResource
    {
        public StaffResource(PuxbayClient client) : base(client) { }
        
        public async Task<PaginatedResponse<Staff>> ListAsync(int page = 1, string role = null)
        {
            var endpoint = $"staff/?page={page}";
            if (!string.IsNullOrEmpty(role))
            {
                endpoint += $"&role={role}";
            }
            return await Client.RequestAsync<PaginatedResponse<Staff>>(HttpMethod.Get, endpoint);
        }
        
        public async Task<Staff> GetAsync(string staffId)
        {
            return await Client.RequestAsync<Staff>(HttpMethod.Get, $"staff/{staffId}/");
        }
        
        public async Task<Staff> CreateAsync(Staff staff)
        {
            return await Client.RequestAsync<Staff>(HttpMethod.Post, "staff/", staff);
        }
        
        public async Task<Staff> UpdateAsync(string staffId, Staff staff)
        {
            return await Client.RequestAsync<Staff>(HttpMethod.Patch, $"staff/{staffId}/", staff);
        }
        
        public async Task DeleteAsync(string staffId)
        {
            await Client.RequestAsync<object>(HttpMethod.Delete, $"staff/{staffId}/");
        }
    }
    
    /// <summary>
    /// Webhooks resource - Webhook configuration operations.
    /// </summary>
    public class WebhooksResource : BaseResource
    {
        public WebhooksResource(PuxbayClient client) : base(client) { }
        
        public async Task<PaginatedResponse<Webhook>> ListAsync(int page = 1)
        {
            return await Client.RequestAsync<PaginatedResponse<Webhook>>(HttpMethod.Get, $"webhooks/?page={page}");
        }
        
        public async Task<Webhook> GetAsync(string webhookId)
        {
            return await Client.RequestAsync<Webhook>(HttpMethod.Get, $"webhooks/{webhookId}/");
        }
        
        public async Task<Webhook> CreateAsync(Webhook webhook)
        {
            return await Client.RequestAsync<Webhook>(HttpMethod.Post, "webhooks/", webhook);
        }
        
        public async Task<Webhook> UpdateAsync(string webhookId, Webhook webhook)
        {
            return await Client.RequestAsync<Webhook>(HttpMethod.Patch, $"webhooks/{webhookId}/", webhook);
        }
        
        public async Task DeleteAsync(string webhookId)
        {
            await Client.RequestAsync<object>(HttpMethod.Delete, $"webhooks/{webhookId}/");
        }
        
        public async Task<PaginatedResponse<WebhookEvent>> ListEventsAsync(string webhookId, int page = 1)
        {
            return await Client.RequestAsync<PaginatedResponse<WebhookEvent>>(
                HttpMethod.Get, 
                $"webhook-logs/?webhook={webhookId}&page={page}"
            );
        }
    }
    
    // Placeholder classes for remaining resources following same pattern
    public class InventoryResource : BaseResource
    {
        public InventoryResource(PuxbayClient client) : base(client) { }
    }
    
    public class ReportsResource : BaseResource
    {
        public ReportsResource(PuxbayClient client) : base(client) { }
    }
    
    public class PurchaseOrdersResource : BaseResource
    {
        public PurchaseOrdersResource(PuxbayClient client) : base(client) { }
    }
    
    public class StockTransfersResource : BaseResource
    {
        public StockTransfersResource(PuxbayClient client) : base(client) { }
    }
    
    public class StocktakesResource : BaseResource
    {
        public StocktakesResource(PuxbayClient client) : base(client) { }
    }
    
    public class CashDrawersResource : BaseResource
    {
        public CashDrawersResource(PuxbayClient client) : base(client) { }
    }
    
    public class ExpensesResource : BaseResource
    {
        public ExpensesResource(PuxbayClient client) : base(client) { }
    }
    
    public class NotificationsResource : BaseResource
    {
        public NotificationsResource(PuxbayClient client) : base(client) { }
    }
    
    public class ReturnsResource : BaseResource
    {
        public ReturnsResource(PuxbayClient client) : base(client) { }
    }
}
