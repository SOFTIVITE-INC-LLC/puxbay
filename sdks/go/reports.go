package puxbay

import "fmt"

// ReportsService handles reports and analytics API calls
type ReportsService struct {
	client *Client
}

// SalesSummary represents sales summary data
type SalesSummary struct {
	TotalSales   float64   `json:"total_sales"`
	TotalOrders  int       `json:"total_orders"`
	AverageOrder float64   `json:"average_order"`
	TopProducts  []Product `json:"top_products"`
}

// SalesSummary retrieves sales summary report
func (s *ReportsService) SalesSummary(startDate, endDate, branchID string) (*SalesSummary, error) {
	endpoint := fmt.Sprintf("reports/sales-summary/?start_date=%s&end_date=%s", startDate, endDate)
	if branchID != "" {
		endpoint = fmt.Sprintf("%s&branch=%s", endpoint, branchID)
	}

	var result SalesSummary
	err := s.client.GET(endpoint, &result)
	return &result, err
}

// ProductPerformance retrieves product performance report
func (s *ReportsService) ProductPerformance(startDate, endDate string, limit int) ([]Product, error) {
	endpoint := fmt.Sprintf("reports/product-performance/?limit=%d", limit)
	if startDate != "" {
		endpoint = fmt.Sprintf("%s&start_date=%s", endpoint, startDate)
	}
	if endDate != "" {
		endpoint = fmt.Sprintf("%s&end_date=%s", endpoint, endDate)
	}

	var result []Product
	err := s.client.GET(endpoint, &result)
	return result, err
}

// CustomerAnalytics represents customer analytics data
type CustomerAnalytics struct {
	NewCustomers         int     `json:"new_customers"`
	RetentionRate        float64 `json:"retention_rate"`
	AverageLifetimeValue float64 `json:"average_lifetime_value"`
}

// CustomerAnalytics retrieves customer analytics report
func (s *ReportsService) CustomerAnalytics(startDate, endDate string) (*CustomerAnalytics, error) {
	endpoint := fmt.Sprintf("reports/customer-analytics/?start_date=%s&end_date=%s", startDate, endDate)

	var result CustomerAnalytics
	err := s.client.GET(endpoint, &result)
	return &result, err
}

// ProfitLoss represents profit & loss data
type ProfitLoss struct {
	Revenue     float64 `json:"revenue"`
	Costs       float64 `json:"costs"`
	GrossProfit float64 `json:"gross_profit"`
	NetProfit   float64 `json:"net_profit"`
}

// ProfitLoss retrieves profit & loss report
func (s *ReportsService) ProfitLoss(startDate, endDate, branchID string) (*ProfitLoss, error) {
	endpoint := fmt.Sprintf("reports/profit-loss/?start_date=%s&end_date=%s", startDate, endDate)
	if branchID != "" {
		endpoint = fmt.Sprintf("%s&branch=%s", endpoint, branchID)
	}

	var result ProfitLoss
	err := s.client.GET(endpoint, &result)
	return &result, err
}
