package puxbay

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net"
	"net/http"
	"time"
)

const (
	defaultBaseURL         = "https://api.puxbay.com/api/v1"
	defaultTimeout         = 30 * time.Second
	defaultMaxIdleConns    = 100
	defaultMaxConnsPerHost = 10
	defaultIdleConnTimeout = 90 * time.Second
	sdkVersion             = "1.0.0"
)

// ClientConfig holds configuration for the Puxbay client
type ClientConfig struct {
	APIKey          string
	BaseURL         string
	Timeout         time.Duration
	MaxRetries      int
	MaxIdleConns    int
	MaxConnsPerHost int
	IdleConnTimeout time.Duration
}

// Client is the main Puxbay API client with performance optimizations
type Client struct {
	APIKey     string
	BaseURL    string
	HTTPClient *http.Client

	Products       *ProductsService
	Orders         *OrdersService
	Customers      *CustomersService
	Inventory      *InventoryService
	Reports        *ReportsService
	Categories     *CategoriesService
	Suppliers      *SuppliersService
	PurchaseOrders *PurchaseOrdersService
	StockTransfers *StockTransfersService
	Stocktakes     *StocktakesService
	CashDrawers    *CashDrawersService
	GiftCards      *GiftCardsService
	Expenses       *ExpensesService
	Branches       *BranchesService
	Staff          *StaffService
	Webhooks       *WebhooksService
	Notifications  *NotificationsService
	Returns        *ReturnsService

	maxRetries int
}

// NewClient creates a new Puxbay API client with default configuration
func NewClient(apiKey string) *Client {
	return NewClientWithConfig(&ClientConfig{
		APIKey:          apiKey,
		BaseURL:         defaultBaseURL,
		Timeout:         defaultTimeout,
		MaxRetries:      3, // Default to 3 retries
		MaxIdleConns:    defaultMaxIdleConns,
		MaxConnsPerHost: defaultMaxConnsPerHost,
		IdleConnTimeout: defaultIdleConnTimeout,
	})
}

// NewClientWithConfig creates a new client with custom configuration
func NewClientWithConfig(config *ClientConfig) *Client {
	if config.APIKey == "" || len(config.APIKey) < 3 || config.APIKey[:3] != "pb_" {
		panic("invalid API key format: must start with 'pb_'")
	}

	// Create HTTP client with connection pooling and timeouts
	transport := &http.Transport{
		MaxIdleConns:        config.MaxIdleConns,
		MaxIdleConnsPerHost: config.MaxConnsPerHost,
		MaxConnsPerHost:     config.MaxConnsPerHost,
		IdleConnTimeout:     config.IdleConnTimeout,
		DisableCompression:  false, // Enable gzip compression
		DialContext: (&net.Dialer{
			Timeout:   10 * time.Second,
			KeepAlive: 30 * time.Second,
		}).DialContext,
		ForceAttemptHTTP2:     true,
		TLSHandshakeTimeout:   10 * time.Second,
		ResponseHeaderTimeout: 10 * time.Second,
		ExpectContinueTimeout: 1 * time.Second,
	}

	httpClient := &http.Client{
		Timeout:   config.Timeout,
		Transport: transport,
	}

	client := &Client{
		APIKey:     config.APIKey,
		BaseURL:    config.BaseURL,
		HTTPClient: httpClient,
		maxRetries: config.MaxRetries,
	}

	// Initialize services
	client.Products = &ProductsService{client: client}
	client.Orders = &OrdersService{client: client}
	client.Customers = &CustomersService{client: client}
	client.Inventory = &InventoryService{client: client}
	client.Reports = &ReportsService{client: client}
	client.Categories = &CategoriesService{client: client}
	client.Suppliers = &SuppliersService{client: client}
	client.PurchaseOrders = &PurchaseOrdersService{client: client}
	client.StockTransfers = &StockTransfersService{client: client}
	client.Stocktakes = &StocktakesService{client: client}
	client.CashDrawers = &CashDrawersService{client: client}
	client.GiftCards = &GiftCardsService{client: client}
	client.Expenses = &ExpensesService{client: client}
	client.Branches = &BranchesService{client: client}
	client.Staff = &StaffService{client: client}
	client.Webhooks = &WebhooksService{client: client}
	client.Notifications = &NotificationsService{client: client}
	client.Returns = &ReturnsService{client: client}

	return client
}

// Request makes an HTTP request to the API with retry logic
func (c *Client) Request(method, endpoint string, body interface{}, result interface{}) error {
	return c.RequestWithContext(context.Background(), method, endpoint, body, result)
}

// RequestWithContext makes an HTTP request with context support and retry logic
func (c *Client) RequestWithContext(ctx context.Context, method, endpoint string, body interface{}, result interface{}) error {
	url := fmt.Sprintf("%s/%s", c.BaseURL, endpoint)

	var reqBody io.Reader
	if body != nil {
		jsonData, err := json.Marshal(body)
		if err != nil {
			return fmt.Errorf("failed to marshal request body: %w", err)
		}
		reqBody = bytes.NewBuffer(jsonData)
	}

	var lastErr error
	for attempt := 0; attempt <= c.maxRetries; attempt++ {
		if attempt > 0 {
			// Exponential backoff: 1s, 2s, 4s, 8s
			backoff := time.Duration(1<<uint(attempt-1)) * time.Second
			select {
			case <-time.After(backoff):
			case <-ctx.Done():
				return ctx.Err()
			}
		}

		req, err := http.NewRequestWithContext(ctx, method, url, reqBody)
		if err != nil {
			return fmt.Errorf("failed to create request: %w", err)
		}

		req.Header.Set("X-API-Key", c.APIKey)
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("User-Agent", fmt.Sprintf("puxbay-go/%s", sdkVersion))
		req.Header.Set("Accept-Encoding", "gzip, deflate")

		resp, err := c.HTTPClient.Do(req)
		if err != nil {
			lastErr = fmt.Errorf("request failed: %w", err)
			// Retry on network errors
			continue
		}
		defer resp.Body.Close()

		// Read response body
		respBody, err := io.ReadAll(resp.Body)
		if err != nil {
			lastErr = fmt.Errorf("failed to read response: %w", err)
			continue
		}

		// Retry on 429 or 5xx errors
		if resp.StatusCode == 429 || resp.StatusCode >= 500 {
			lastErr = handleErrorResponse(resp.StatusCode, respBody)
			continue
		}

		// Handle other errors
		if resp.StatusCode >= 400 {
			return handleErrorResponse(resp.StatusCode, respBody)
		}

		// Parse successful response
		if result != nil && len(respBody) > 0 {
			if err := json.Unmarshal(respBody, result); err != nil {
				return fmt.Errorf("failed to parse response: %w", err)
			}
		}

		return nil
	}

	return lastErr
}

// GET makes a GET request
func (c *Client) GET(endpoint string, result interface{}) error {
	return c.Request(http.MethodGet, endpoint, nil, result)
}

// POST makes a POST request
func (c *Client) POST(endpoint string, body, result interface{}) error {
	return c.Request(http.MethodPost, endpoint, body, result)
}

// PUT makes a PUT request
func (c *Client) PUT(endpoint string, body, result interface{}) error {
	return c.Request(http.MethodPut, endpoint, body, result)
}

// PATCH makes a PATCH request
func (c *Client) PATCH(endpoint string, body, result interface{}) error {
	return c.Request(http.MethodPatch, endpoint, body, result)
}

// DELETE makes a DELETE request
func (c *Client) DELETE(endpoint string) error {
	return c.Request(http.MethodDelete, endpoint, nil, nil)
}
