package puxbay

import (
	"fmt"
)

// OrdersService handles order-related API calls
type OrdersService struct {
	client *Client
}

// OrderListParams contains parameters for listing orders
type OrderListParams struct {
	Page       int    `json:"page,omitempty"`
	PageSize   int    `json:"page_size,omitempty"`
	Status     string `json:"status,omitempty"`
	CustomerID string `json:"customer,omitempty"`
}

// List retrieves a list of orders
func (s *OrdersService) List(params *OrderListParams) (*PaginatedResponse, error) {
	endpoint := "orders/"
	if params != nil {
		endpoint = fmt.Sprintf("%s?page=%d&page_size=%d", endpoint, params.Page, params.PageSize)
		if params.Status != "" {
			endpoint = fmt.Sprintf("%s&status=%s", endpoint, params.Status)
		}
		if params.CustomerID != "" {
			endpoint = fmt.Sprintf("%s&customer=%s", endpoint, params.CustomerID)
		}
	}

	var result PaginatedResponse
	err := s.client.GET(endpoint, &result)
	return &result, err
}

// Get retrieves a specific order by ID
func (s *OrdersService) Get(orderID string) (*Order, error) {
	var order Order
	err := s.client.GET(fmt.Sprintf("orders/%s/", orderID), &order)
	return &order, err
}

// Create creates a new order
func (s *OrdersService) Create(order *Order) (*Order, error) {
	var result Order
	err := s.client.POST("orders/", order, &result)
	return &result, err
}

// Update updates an existing order
func (s *OrdersService) Update(orderID string, order *Order) (*Order, error) {
	var result Order
	err := s.client.PATCH(fmt.Sprintf("orders/%s/", orderID), order, &result)
	return &result, err
}

// Cancel cancels an order
func (s *OrdersService) Cancel(orderID string, reason string) (*Order, error) {
	body := map[string]interface{}{
		"status": "cancelled",
	}
	if reason != "" {
		body["cancellation_reason"] = reason
	}
	var result Order
	err := s.client.PATCH(fmt.Sprintf("orders/%s/", orderID), body, &result)
	return &result, err
}
