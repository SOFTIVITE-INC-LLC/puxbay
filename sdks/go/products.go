package puxbay

import (
	"fmt"
)

// ProductsService handles product-related API calls
type ProductsService struct {
	client *Client
}

// ListParams contains parameters for listing products
type ListParams struct {
	Page     int    `json:"page,omitempty"`
	PageSize int    `json:"page_size,omitempty"`
	Search   string `json:"search,omitempty"`
}

// PaginatedResponse represents a paginated API response
type PaginatedResponse struct {
	Count    int         `json:"count"`
	Next     *string     `json:"next"`
	Previous *string     `json:"previous"`
	Results  interface{} `json:"results"`
}

// List retrieves a list of products
func (s *ProductsService) List(params *ListParams) (*PaginatedResponse, error) {
	endpoint := "products/"
	if params != nil {
		endpoint = fmt.Sprintf("%s?page=%d&page_size=%d", endpoint, params.Page, params.PageSize)
		if params.Search != "" {
			endpoint = fmt.Sprintf("%s&search=%s", endpoint, params.Search)
		}
	}

	var result PaginatedResponse
	err := s.client.GET(endpoint, &result)
	return &result, err
}

// Get retrieves a specific product by ID
func (s *ProductsService) Get(productID string) (*Product, error) {
	var product Product
	err := s.client.GET(fmt.Sprintf("products/%s/", productID), &product)
	return &product, err
}

// Create creates a new product
func (s *ProductsService) Create(product *Product) (*Product, error) {
	var result Product
	err := s.client.POST("products/", product, &result)
	return &result, err
}

// Update updates an existing product
func (s *ProductsService) Update(productID string, product *Product) (*Product, error) {
	var result Product
	err := s.client.PATCH(fmt.Sprintf("products/%s/", productID), product, &result)
	return &result, err
}

// Delete deletes a product
func (s *ProductsService) Delete(productID string) error {
	return s.client.DELETE(fmt.Sprintf("products/%s/", productID))
}

// AdjustStock adjusts the stock quantity of a product
func (s *ProductsService) AdjustStock(productID string, quantity int, reason string) (*Product, error) {
	body := map[string]interface{}{
		"quantity": quantity,
		"reason":   reason,
	}
	var result Product
	err := s.client.POST(fmt.Sprintf("products/%s/adjust_stock/", productID), body, &result)
	return &result, err
}
