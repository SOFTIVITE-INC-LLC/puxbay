package puxbay

import (
	"fmt"
)

// CustomersService handles customer-related API calls
type CustomersService struct {
	client *Client
}

// List retrieves a list of customers
func (s *CustomersService) List(params *ListParams) (*PaginatedResponse, error) {
	endpoint := "customers/"
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

// Get retrieves a specific customer by ID
func (s *CustomersService) Get(customerID string) (*Customer, error) {
	var customer Customer
	err := s.client.GET(fmt.Sprintf("customers/%s/", customerID), &customer)
	return &customer, err
}

// Create creates a new customer
func (s *CustomersService) Create(customer *Customer) (*Customer, error) {
	var result Customer
	err := s.client.POST("customers/", customer, &result)
	return &result, err
}

// Update updates an existing customer
func (s *CustomersService) Update(customerID string, customer *Customer) (*Customer, error) {
	var result Customer
	err := s.client.PATCH(fmt.Sprintf("customers/%s/", customerID), customer, &result)
	return &result, err
}

// Delete deletes a customer
func (s *CustomersService) Delete(customerID string) error {
	return s.client.DELETE(fmt.Sprintf("customers/%s/", customerID))
}

// AddLoyaltyPoints adds loyalty points to a customer
func (s *CustomersService) AddLoyaltyPoints(customerID string, points int, description string) (*Customer, error) {
	body := map[string]interface{}{
		"points":      points,
		"description": description,
	}
	var result Customer
	err := s.client.POST(fmt.Sprintf("customers/%s/add_loyalty_points/", customerID), body, &result)
	return &result, err
}

// AddStoreCredit adds store credit to a customer
func (s *CustomersService) AddStoreCredit(customerID string, amount float64, description string) (*Customer, error) {
	body := map[string]interface{}{
		"amount":      amount,
		"description": description,
	}
	var result Customer
	err := s.client.POST(fmt.Sprintf("customers/%s/add_store_credit/", customerID), body, &result)
	return &result, err
}
