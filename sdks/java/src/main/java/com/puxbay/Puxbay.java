package com.puxbay;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.puxbay.exceptions.*;
import com.puxbay.resources.*;
import okhttp3.*;
import java.io.IOException;
import java.lang.reflect.Type;
import java.util.concurrent.TimeUnit;

/**
 * Main Puxbay API client.
 */
public class Puxbay {
    private static final String DEFAULT_BASE_URL = "https://api.puxbay.com/api/v1";
    private static final String SDK_VERSION = "1.0.0";
    
    private final OkHttpClient httpClient;
    private final Gson gson;
    private final String apiKey;
    private final String baseUrl;
    private final int maxRetries;
    
    // Resource clients
    private final ProductsResource products;
    private final OrdersResource orders;
    private final CustomersResource customers;
    private final InventoryResource inventory;
    private final ReportsResource reports;
    private final CategoriesResource categories;
    private final SuppliersResource suppliers;
    private final PurchaseOrdersResource purchaseOrders;
    private final StockTransfersResource stockTransfers;
    private final StocktakesResource stocktakes;
    private final CashDrawersResource cashDrawers;
    private final GiftCardsResource giftCards;
    private final ExpensesResource expenses;
    private final BranchesResource branches;
    private final StaffResource staff;
    private final WebhooksResource webhooks;
    private final NotificationsResource notifications;
    private final ReturnsResource returns;
    
    public Puxbay(PuxbayConfig config) {
        if (config.getApiKey() == null || !config.getApiKey().startsWith("pb_")) {
            throw new IllegalArgumentException("Invalid API key format. Must start with 'pb_'");
        }
        
        this.apiKey = config.getApiKey();
        this.baseUrl = config.getBaseUrl() != null ? config.getBaseUrl() : DEFAULT_BASE_URL;
        this.maxRetries = config.getMaxRetries();
        
        ConnectionPool connectionPool = new ConnectionPool(
            config.getMaxIdleConnections(),
            config.getKeepAliveDuration(),
            TimeUnit.SECONDS
        );
        
        this.httpClient = new OkHttpClient.Builder()
            .connectionPool(connectionPool)
            .connectTimeout(config.getTimeout(), TimeUnit.SECONDS)
            .readTimeout(config.getTimeout(), TimeUnit.SECONDS)
            .writeTimeout(config.getTimeout(), TimeUnit.SECONDS)
            .addInterceptor(new RetryInterceptor(maxRetries))
            .addInterceptor(chain -> {
                Request original = chain.request();
                Request request = original.newBuilder()
                    .header("X-API-Key", apiKey)
                    .header("Content-Type", "application/json")
                    .header("User-Agent", "puxbay-java/" + SDK_VERSION)
                    .header("Accept-Encoding", "gzip, deflate")
                    .build();
                return chain.proceed(request);
            })
            .build();
        
        this.gson = new GsonBuilder()
            .setDateFormat("yyyy-MM-dd'T'HH:mm:ss")
            .create();
        
        // Initialize resource clients
        this.products = new ProductsResource(this);
        this.orders = new OrdersResource(this);
        this.customers = new CustomersResource(this);
        this.inventory = new InventoryResource(this);
        this.reports = new ReportsResource(this);
        this.categories = new CategoriesResource(this);
        this.suppliers = new SuppliersResource(this);
        this.purchaseOrders = new PurchaseOrdersResource(this);
        this.stockTransfers = new StockTransfersResource(this);
        this.stocktakes = new StocktakesResource(this);
        this.cashDrawers = new CashDrawersResource(this);
        this.giftCards = new GiftCardsResource(this);
        this.expenses = new ExpensesResource(this);
        this.branches = new BranchesResource(this);
        this.staff = new StaffResource(this);
        this.webhooks = new WebhooksResource(this);
        this.notifications = new NotificationsResource(this);
        this.returns = new ReturnsResource(this);
    }
    
    // Resource accessors
    public ProductsResource products() { return products; }
    public OrdersResource orders() { return orders; }
    public CustomersResource customers() { return customers; }
    public InventoryResource inventory() { return inventory; }
    public ReportsResource reports() { return reports; }
    public CategoriesResource categories() { return categories; }
    public SuppliersResource suppliers() { return suppliers; }
    public PurchaseOrdersResource purchaseOrders() { return purchaseOrders; }
    public StockTransfersResource stockTransfers() { return stockTransfers; }
    public StocktakesResource stocktakes() { return stocktakes; }
    public CashDrawersResource cashDrawers() { return cashDrawers; }
    public GiftCardsResource giftCards() { return giftCards; }
    public ExpensesResource expenses() { return expenses; }
    public BranchesResource branches() { return branches; }
    public StaffResource staff() { return staff; }
    public WebhooksResource webhooks() { return webhooks; }
    public NotificationsResource notifications() { return notifications; }
    public ReturnsResource returns() { return returns; }
    
    public <T> T request(String method, String endpoint, Object body, Class<T> responseType) throws PuxbayException {
        return request(method, endpoint, body, (Type) responseType);
    }
    
    public <T> T request(String method, String endpoint, Object body, Type responseType) throws PuxbayException {
        String url = baseUrl + "/" + endpoint;
        
        Request.Builder requestBuilder = new Request.Builder().url(url);
        
        if (body != null) {
            String json = gson.toJson(body);
            RequestBody requestBody = RequestBody.create(json, MediaType.parse("application/json"));
            requestBuilder.method(method, requestBody);
        } else {
            if ("GET".equals(method)) {
                requestBuilder.get();
            } else if ("DELETE".equals(method)) {
                requestBuilder.delete();
            } else {
                requestBuilder.method(method, RequestBody.create("", null));
            }
        }
        
        try (Response response = httpClient.newCall(requestBuilder.build()).execute()) {
            String responseBody = response.body() != null ? response.body().string() : "";
            
            if (!response.isSuccessful()) {
                handleErrorResponse(response.code(), responseBody);
            }
            
            if (responseType == Void.class || responseBody.isEmpty()) {
                return null;
            }
            
            return gson.fromJson(responseBody, responseType);
        } catch (IOException e) {
            throw new PuxbayException("Network error: " + e.getMessage(), 0);
        }
    }
    
    private void handleErrorResponse(int statusCode, String body) throws PuxbayException {
        String message = "Unknown error";
        try {
            ErrorResponse error = gson.fromJson(body, ErrorResponse.class);
            message = error.getDetail() != null ? error.getDetail() : error.getMessage();
        } catch (Exception ignored) {
        }
        
        switch (statusCode) {
            case 401:
                throw new AuthenticationException(message, statusCode);
            case 429:
                throw new RateLimitException(message, statusCode);
            case 400:
                throw new ValidationException(message, statusCode);
            case 404:
                throw new NotFoundException(message, statusCode);
            default:
                if (statusCode >= 500) {
                    throw new ServerException(message, statusCode);
                }
                throw new PuxbayException(message, statusCode);
        }
    }
    
    public Gson getGson() {
        return gson;
    }
    
    public void close() {
        httpClient.dispatcher().executorService().shutdown();
        httpClient.connectionPool().evictAll();
    }
    
    private static class ErrorResponse {
        private String detail;
        private String message;
        public String getDetail() { return detail; }
        public String getMessage() { return message; }
    }
    
    private static class RetryInterceptor implements Interceptor {
        private final int maxRetries;
        public RetryInterceptor(int maxRetries) { this.maxRetries = maxRetries; }
        @Override
        public Response intercept(Chain chain) throws IOException {
            Request request = chain.request();
            Response response = null;
            IOException lastException = null;
            for (int attempt = 0; attempt <= maxRetries; attempt++) {
                try {
                    if (response != null) response.close();
                    response = chain.proceed(request);
                    if (response.code() != 429 && response.code() < 500) return response;
                    if (attempt < maxRetries) {
                        long delay = (long) Math.pow(2, attempt) * 1000;
                        Thread.sleep(delay);
                    }
                } catch (Exception e) {
                    if (e instanceof InterruptedException) Thread.currentThread().interrupt();
                    lastException = new IOException("Retry failed", e);
                }
            }
            if (lastException != null) throw lastException;
            return response;
        }
    }
}
