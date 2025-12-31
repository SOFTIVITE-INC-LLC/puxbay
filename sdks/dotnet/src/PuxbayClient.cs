using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Polly;
using Polly.Retry;
using Puxbay.SDK.Exceptions;
using Puxbay.SDK.Resources;

namespace Puxbay.SDK
{
    /// <summary>
    /// Main Puxbay API client with connection pooling and retry logic.
    /// </summary>
    /// <example>
    /// <code>
    /// var config = new PuxbayConfig
    /// {
    ///     ApiKey = "pb_your_api_key_here",
    ///     MaxRetries = 5,
    ///     Timeout = TimeSpan.FromSeconds(30)
    /// };
    /// 
    /// using var client = new PuxbayClient(config);
    /// var products = await client.Products.ListAsync(1, 20);
    /// </code>
    /// </example>
    public class PuxbayClient : IDisposable
    {
        private const string DefaultBaseUrl = "https://api.puxbay.com/api/v1";
        private const string SdkVersion = "1.0.0";
        
        private readonly HttpClient _httpClient;
        private readonly AsyncRetryPolicy<HttpResponseMessage> _retryPolicy;
        private readonly string _apiKey;
        private readonly string _baseUrl;
        
        // Resource clients
        public ProductsResource Products { get; }
        public OrdersResource Orders { get; }
        public CustomersResource Customers { get; }
        public InventoryResource Inventory { get; }
        public ReportsResource Reports { get; }
        public CategoriesResource Categories { get; }
        public SuppliersResource Suppliers { get; }
        public PurchaseOrdersResource PurchaseOrders { get; }
        public StockTransfersResource StockTransfers { get; }
        public StocktakesResource Stocktakes { get; }
        public CashDrawersResource CashDrawers { get; }
        public GiftCardsResource GiftCards { get; }
        public ExpensesResource Expenses { get; }
        public BranchesResource Branches { get; }
        public StaffResource Staff { get; }
        public WebhooksResource Webhooks { get; }
        public NotificationsResource Notifications { get; }
        public ReturnsResource Returns { get; }
        
        /// <summary>
        /// Creates a new Puxbay client with the given configuration.
        /// </summary>
        /// <param name="config">Client configuration</param>
        /// <exception cref="ArgumentException">Thrown when API key is invalid</exception>
        public PuxbayClient(PuxbayConfig config)
        {
            if (string.IsNullOrEmpty(config.ApiKey) || !config.ApiKey.StartsWith("pb_"))
            {
                throw new ArgumentException("Invalid API key format. Must start with 'pb_'", nameof(config.ApiKey));
            }
            
            _apiKey = config.ApiKey;
            _baseUrl = config.BaseUrl ?? DefaultBaseUrl;
            
            // Configure HTTP client with connection pooling
            var handler = new SocketsHttpHandler
            {
                PooledConnectionLifetime = TimeSpan.FromMinutes(5),
                PooledConnectionIdleTimeout = TimeSpan.FromMinutes(2),
                MaxConnectionsPerServer = config.MaxConnectionsPerServer,
                AutomaticDecompression = System.Net.DecompressionMethods.GZip | System.Net.DecompressionMethods.Deflate
            };
            
            _httpClient = new HttpClient(handler)
            {
                Timeout = config.Timeout,
                BaseAddress = new Uri(_baseUrl)
            };
            
            _httpClient.DefaultRequestHeaders.Add("X-API-Key", _apiKey);
            _httpClient.DefaultRequestHeaders.Add("User-Agent", $"puxbay-dotnet/{SdkVersion}");
            _httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            _httpClient.DefaultRequestHeaders.AcceptEncoding.Add(new StringWithQualityHeaderValue("gzip"));
            _httpClient.DefaultRequestHeaders.AcceptEncoding.Add(new StringWithQualityHeaderValue("deflate"));
            
            // Configure retry policy with exponential backoff
            _retryPolicy = Policy
                .HandleResult<HttpResponseMessage>(r => 
                    r.StatusCode == System.Net.HttpStatusCode.TooManyRequests ||
                    (int)r.StatusCode >= 500)
                .WaitAndRetryAsync(
                    config.MaxRetries,
                    retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)),
                    onRetry: (outcome, timespan, retryCount, context) =>
                    {
                        // Log retry attempt if needed
                    });
            
            // Initialize resource clients
            Products = new ProductsResource(this);
            Orders = new OrdersResource(this);
            Customers = new CustomersResource(this);
            Inventory = new InventoryResource(this);
            Reports = new ReportsResource(this);
            Categories = new CategoriesResource(this);
            Suppliers = new SuppliersResource(this);
            PurchaseOrders = new PurchaseOrdersResource(this);
            StockTransfers = new StockTransfersResource(this);
            Stocktakes = new StocktakesResource(this);
            CashDrawers = new CashDrawersResource(this);
            GiftCards = new GiftCardsResource(this);
            Expenses = new ExpensesResource(this);
            Branches = new BranchesResource(this);
            Staff = new StaffResource(this);
            Webhooks = new WebhooksResource(this);
            Notifications = new NotificationsResource(this);
            Returns = new ReturnsResource(this);
        }
        
        /// <summary>
        /// Makes an HTTP request to the API.
        /// </summary>
        internal async Task<T> RequestAsync<T>(HttpMethod method, string endpoint, object body = null)
        {
            var request = new HttpRequestMessage(method, endpoint);
            
            if (body != null)
            {
                var json = JsonConvert.SerializeObject(body, new JsonSerializerSettings 
                { 
                    NullValueHandling = NullValueHandling.Ignore 
                });
                request.Content = new StringContent(json, Encoding.UTF8, "application/json");
            }
            
            var response = await _retryPolicy.ExecuteAsync(() => _httpClient.SendAsync(request));
            
            var content = await response.Content.ReadAsStringAsync();
            
            if (!response.IsSuccessStatusCode)
            {
                HandleErrorResponse((int)response.StatusCode, content);
            }
            
            if (typeof(T) == typeof(object) || string.IsNullOrEmpty(content))
            {
                return default;
            }
            
            return JsonConvert.DeserializeObject<T>(content);
        }

        internal async Task<T> GetAsync<T>(string endpoint)
        {
            return await RequestAsync<T>(HttpMethod.Get, endpoint);
        }

        internal async Task<T> PostAsync<T>(string endpoint, object body)
        {
            return await RequestAsync<T>(HttpMethod.Post, endpoint, body);
        }

        internal async Task<T> PatchAsync<T>(string endpoint, object body)
        {
            return await RequestAsync<T>(new HttpMethod("PATCH"), endpoint, body);
        }

        internal async Task DeleteAsync(string endpoint)
        {
            await RequestAsync<object>(HttpMethod.Delete, endpoint);
        }
        
        private void HandleErrorResponse(int statusCode, string body)
        {
            string message = "Unknown error";
            try
            {
                var error = JsonConvert.DeserializeObject<ErrorResponse>(body);
                message = error?.Detail ?? error?.Message ?? message;
            }
            catch { }
            
            switch (statusCode)
            {
                case 401:
                    throw new AuthenticationException(message, statusCode);
                case 429:
                    throw new RateLimitException(message, statusCode);
                case 400:
                    throw new ValidationException(message, statusCode);
                case 404:
                    throw new NotFoundException(message, statusCode);
                default:
                    if (statusCode >= 500)
                    {
                        throw new ServerException(message, statusCode);
                    }
                    throw new PuxbayException(message, statusCode);
            }
        }
        
        public void Dispose()
        {
            _httpClient?.Dispose();
        }
        
        private class ErrorResponse
        {
            public string Detail { get; set; }
            public string Message { get; set; }
        }
    }
}
