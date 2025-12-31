package puxbay

import "fmt"

// InventoryService handles inventory-related API calls
type InventoryService struct {
	client *Client
}

// StockLevel represents current stock information
type StockLevel struct {
	ProductID string `json:"product_id"`
	Quantity  int    `json:"quantity"`
	Branch    string `json:"branch"`
}

// GetStockLevels retrieves current stock levels
func (s *InventoryService) GetStockLevels(branchID string) ([]StockLevel, error) {
	endpoint := "inventory/stock-levels/"
	if branchID != "" {
		endpoint = fmt.Sprintf("%s?branch=%s", endpoint, branchID)
	}

	var result []StockLevel
	err := s.client.GET(endpoint, &result)
	return result, err
}

// GetLowStock retrieves products with low stock
func (s *InventoryService) GetLowStock(threshold int) ([]Product, error) {
	endpoint := fmt.Sprintf("inventory/low-stock/?threshold=%d", threshold)
	var result []Product
	err := s.client.GET(endpoint, &result)
	return result, err
}

// CreateTransfer creates a new stock transfer
func (s *InventoryService) CreateTransfer(transfer *StockTransfer) (*StockTransfer, error) {
	var result StockTransfer
	err := s.client.POST("stock-transfers/", transfer, &result)
	return &result, err
}

// ListTransfers retrieves a list of stock transfers
func (s *InventoryService) ListTransfers(page int, status string) (*PaginatedResponse, error) {
	endpoint := fmt.Sprintf("stock-transfers/?page=%d", page)
	if status != "" {
		endpoint = fmt.Sprintf("%s&status=%s", endpoint, status)
	}

	var result PaginatedResponse
	err := s.client.GET(endpoint, &result)
	return &result, err
}
