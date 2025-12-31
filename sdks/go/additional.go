package puxbay

// Complete resource services with all CRUD methods

import "fmt"

// ============================================================================
// Categories Service
// ============================================================================

// CategoriesService handles category-related API calls
type CategoriesService struct {
	client *Client
}

func (s *CategoriesService) List(page int) (*PaginatedResponse, error) {
	endpoint := fmt.Sprintf("categories/?page=%d", page)
	var result PaginatedResponse
	err := s.client.GET(endpoint, &result)
	return &result, err
}

func (s *CategoriesService) Get(categoryID string) (*Category, error) {
	var category Category
	err := s.client.GET(fmt.Sprintf("categories/%s/", categoryID), &category)
	return &category, err
}

func (s *CategoriesService) Create(category *Category) (*Category, error) {
	var result Category
	err := s.client.POST("categories/", category, &result)
	return &result, err
}

func (s *CategoriesService) Update(categoryID string, category *Category) (*Category, error) {
	var result Category
	err := s.client.PATCH(fmt.Sprintf("categories/%s/", categoryID), category, &result)
	return &result, err
}

func (s *CategoriesService) Delete(categoryID string) error {
	return s.client.DELETE(fmt.Sprintf("categories/%s/", categoryID))
}

// ============================================================================
// Suppliers Service
// ============================================================================

// SuppliersService handles supplier-related API calls
type SuppliersService struct {
	client *Client
}

func (s *SuppliersService) List(params *ListParams) (*PaginatedResponse, error) {
	endpoint := "suppliers/"
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

func (s *SuppliersService) Get(supplierID string) (*Supplier, error) {
	var supplier Supplier
	err := s.client.GET(fmt.Sprintf("suppliers/%s/", supplierID), &supplier)
	return &supplier, err
}

func (s *SuppliersService) Create(supplier *Supplier) (*Supplier, error) {
	var result Supplier
	err := s.client.POST("suppliers/", supplier, &result)
	return &result, err
}

func (s *SuppliersService) Update(supplierID string, supplier *Supplier) (*Supplier, error) {
	var result Supplier
	err := s.client.PATCH(fmt.Sprintf("suppliers/%s/", supplierID), supplier, &result)
	return &result, err
}

func (s *SuppliersService) Delete(supplierID string) error {
	return s.client.DELETE(fmt.Sprintf("suppliers/%s/", supplierID))
}

// ============================================================================
// Purchase Orders Service
// ============================================================================

// PurchaseOrdersService handles purchase order-related API calls
type PurchaseOrdersService struct {
	client *Client
}

func (s *PurchaseOrdersService) List(page int, status string) (*PaginatedResponse, error) {
	endpoint := fmt.Sprintf("purchase-orders/?page=%d", page)
	if status != "" {
		endpoint = fmt.Sprintf("%s&status=%s", endpoint, status)
	}
	var result PaginatedResponse
	err := s.client.GET(endpoint, &result)
	return &result, err
}

func (s *PurchaseOrdersService) Get(poID string) (*PurchaseOrder, error) {
	var po PurchaseOrder
	err := s.client.GET(fmt.Sprintf("purchase-orders/%s/", poID), &po)
	return &po, err
}

func (s *PurchaseOrdersService) Create(po *PurchaseOrder) (*PurchaseOrder, error) {
	var result PurchaseOrder
	err := s.client.POST("purchase-orders/", po, &result)
	return &result, err
}

func (s *PurchaseOrdersService) Update(poID string, po *PurchaseOrder) (*PurchaseOrder, error) {
	var result PurchaseOrder
	err := s.client.PATCH(fmt.Sprintf("purchase-orders/%s/", poID), po, &result)
	return &result, err
}

func (s *PurchaseOrdersService) Receive(poID string, items []PurchaseOrderItem) (*PurchaseOrder, error) {
	body := map[string]interface{}{"items": items}
	var result PurchaseOrder
	err := s.client.POST(fmt.Sprintf("purchase-orders/%s/receive/", poID), body, &result)
	return &result, err
}

// ============================================================================
// Stock Transfers Service
// ============================================================================

// StockTransfersService handles stock transfer-related API calls
type StockTransfersService struct {
	client *Client
}

func (s *StockTransfersService) List(page int, status string) (*PaginatedResponse, error) {
	endpoint := fmt.Sprintf("stock-transfers/?page=%d", page)
	if status != "" {
		endpoint = fmt.Sprintf("%s&status=%s", endpoint, status)
	}
	var result PaginatedResponse
	err := s.client.GET(endpoint, &result)
	return &result, err
}

func (s *StockTransfersService) Get(transferID string) (*StockTransfer, error) {
	var transfer StockTransfer
	err := s.client.GET(fmt.Sprintf("stock-transfers/%s/", transferID), &transfer)
	return &transfer, err
}

func (s *StockTransfersService) Create(transfer *StockTransfer) (*StockTransfer, error) {
	var result StockTransfer
	err := s.client.POST("stock-transfers/", transfer, &result)
	return &result, err
}

func (s *StockTransfersService) Complete(transferID string) (*StockTransfer, error) {
	var result StockTransfer
	err := s.client.POST(fmt.Sprintf("stock-transfers/%s/complete/", transferID), nil, &result)
	return &result, err
}

// ============================================================================
// Stocktakes Service
// ============================================================================

// StocktakesService handles stocktake-related API calls
type StocktakesService struct {
	client *Client
}

func (s *StocktakesService) List(page int) (*PaginatedResponse, error) {
	endpoint := fmt.Sprintf("stocktakes/?page=%d", page)
	var result PaginatedResponse
	err := s.client.GET(endpoint, &result)
	return &result, err
}

func (s *StocktakesService) Get(stocktakeID string) (*StocktakeSession, error) {
	var stocktake StocktakeSession
	err := s.client.GET(fmt.Sprintf("stocktakes/%s/", stocktakeID), &stocktake)
	return &stocktake, err
}

func (s *StocktakesService) Create(stocktake *StocktakeSession) (*StocktakeSession, error) {
	var result StocktakeSession
	err := s.client.POST("stocktakes/", stocktake, &result)
	return &result, err
}

func (s *StocktakesService) Complete(stocktakeID string) (*StocktakeSession, error) {
	var result StocktakeSession
	err := s.client.POST(fmt.Sprintf("stocktakes/%s/complete/", stocktakeID), nil, &result)
	return &result, err
}

// ============================================================================
// Cash Drawers Service
// ============================================================================

// CashDrawersService handles cash drawer-related API calls
type CashDrawersService struct {
	client *Client
}

func (s *CashDrawersService) List(page int) (*PaginatedResponse, error) {
	endpoint := fmt.Sprintf("cash-drawers/?page=%d", page)
	var result PaginatedResponse
	err := s.client.GET(endpoint, &result)
	return &result, err
}

func (s *CashDrawersService) Get(drawerID string) (*CashDrawerSession, error) {
	var drawer CashDrawerSession
	err := s.client.GET(fmt.Sprintf("cash-drawers/%s/", drawerID), &drawer)
	return &drawer, err
}

func (s *CashDrawersService) Open(drawer *CashDrawerSession) (*CashDrawerSession, error) {
	var result CashDrawerSession
	err := s.client.POST("cash-drawers/", drawer, &result)
	return &result, err
}

func (s *CashDrawersService) Close(drawerID string, actualCash float64) (*CashDrawerSession, error) {
	body := map[string]interface{}{"actual_cash": actualCash}
	var result CashDrawerSession
	err := s.client.POST(fmt.Sprintf("cash-drawers/%s/close/", drawerID), body, &result)
	return &result, err
}

// ============================================================================
// Gift Cards Service
// ============================================================================

// GiftCardsService handles gift card-related API calls
type GiftCardsService struct {
	client *Client
}

func (s *GiftCardsService) List(page int, status string) (*PaginatedResponse, error) {
	endpoint := fmt.Sprintf("gift-cards/?page=%d", page)
	if status != "" {
		endpoint = fmt.Sprintf("%s&status=%s", endpoint, status)
	}
	var result PaginatedResponse
	err := s.client.GET(endpoint, &result)
	return &result, err
}

func (s *GiftCardsService) Get(cardID string) (*GiftCard, error) {
	var card GiftCard
	err := s.client.GET(fmt.Sprintf("gift-cards/%s/", cardID), &card)
	return &card, err
}

func (s *GiftCardsService) Create(card *GiftCard) (*GiftCard, error) {
	var result GiftCard
	err := s.client.POST("gift-cards/", card, &result)
	return &result, err
}

func (s *GiftCardsService) Redeem(cardID string, amount float64) (*GiftCard, error) {
	body := map[string]interface{}{"amount": amount}
	var result GiftCard
	err := s.client.POST(fmt.Sprintf("gift-cards/%s/redeem/", cardID), body, &result)
	return &result, err
}

func (s *GiftCardsService) CheckBalance(cardCode string) (*GiftCard, error) {
	endpoint := fmt.Sprintf("gift-cards/check-balance/?code=%s", cardCode)
	var result GiftCard
	err := s.client.GET(endpoint, &result)
	return &result, err
}

// ============================================================================
// Expenses Service
// ============================================================================

// ExpensesService handles expense-related API calls
type ExpensesService struct {
	client *Client
}

func (s *ExpensesService) List(page int, category string) (*PaginatedResponse, error) {
	endpoint := fmt.Sprintf("expenses/?page=%d", page)
	if category != "" {
		endpoint = fmt.Sprintf("%s&category=%s", endpoint, category)
	}
	var result PaginatedResponse
	err := s.client.GET(endpoint, &result)
	return &result, err
}

func (s *ExpensesService) Get(expenseID string) (*Expense, error) {
	var expense Expense
	err := s.client.GET(fmt.Sprintf("expenses/%s/", expenseID), &expense)
	return &expense, err
}

func (s *ExpensesService) Create(expense *Expense) (*Expense, error) {
	var result Expense
	err := s.client.POST("expenses/", expense, &result)
	return &result, err
}

func (s *ExpensesService) Update(expenseID string, expense *Expense) (*Expense, error) {
	var result Expense
	err := s.client.PATCH(fmt.Sprintf("expenses/%s/", expenseID), expense, &result)
	return &result, err
}

func (s *ExpensesService) Delete(expenseID string) error {
	return s.client.DELETE(fmt.Sprintf("expenses/%s/", expenseID))
}

func (s *ExpensesService) ListCategories() ([]ExpenseCategory, error) {
	var result []ExpenseCategory
	err := s.client.GET("expense-categories/", &result)
	return result, err
}

// ============================================================================
// Branches Service
// ============================================================================

// BranchesService handles branch-related API calls
type BranchesService struct {
	client *Client
}

func (s *BranchesService) List(page int) (*PaginatedResponse, error) {
	endpoint := fmt.Sprintf("branches/?page=%d", page)
	var result PaginatedResponse
	err := s.client.GET(endpoint, &result)
	return &result, err
}

func (s *BranchesService) Get(branchID string) (*Branch, error) {
	var branch Branch
	err := s.client.GET(fmt.Sprintf("branches/%s/", branchID), &branch)
	return &branch, err
}

func (s *BranchesService) Create(branch *Branch) (*Branch, error) {
	var result Branch
	err := s.client.POST("branches/", branch, &result)
	return &result, err
}

func (s *BranchesService) Update(branchID string, branch *Branch) (*Branch, error) {
	var result Branch
	err := s.client.PATCH(fmt.Sprintf("branches/%s/", branchID), branch, &result)
	return &result, err
}

func (s *BranchesService) Delete(branchID string) error {
	return s.client.DELETE(fmt.Sprintf("branches/%s/", branchID))
}

// ============================================================================
// Staff Service
// ============================================================================

// StaffService handles staff-related API calls
type StaffService struct {
	client *Client
}

func (s *StaffService) List(page int, role string) (*PaginatedResponse, error) {
	endpoint := fmt.Sprintf("staff/?page=%d", page)
	if role != "" {
		endpoint = fmt.Sprintf("%s&role=%s", endpoint, role)
	}
	var result PaginatedResponse
	err := s.client.GET(endpoint, &result)
	return &result, err
}

func (s *StaffService) Get(staffID string) (*StaffMember, error) {
	var staff StaffMember
	err := s.client.GET(fmt.Sprintf("staff/%s/", staffID), &staff)
	return &staff, err
}

func (s *StaffService) Create(staff *StaffMember) (*StaffMember, error) {
	var result StaffMember
	err := s.client.POST("staff/", staff, &result)
	return &result, err
}

func (s *StaffService) Update(staffID string, staff *StaffMember) (*StaffMember, error) {
	var result StaffMember
	err := s.client.PATCH(fmt.Sprintf("staff/%s/", staffID), staff, &result)
	return &result, err
}

func (s *StaffService) Delete(staffID string) error {
	return s.client.DELETE(fmt.Sprintf("staff/%s/", staffID))
}

// ============================================================================
// Webhooks Service
// ============================================================================

// WebhooksService handles webhook-related API calls
type WebhooksService struct {
	client *Client
}

func (s *WebhooksService) List(page int) (*PaginatedResponse, error) {
	endpoint := fmt.Sprintf("webhooks/?page=%d", page)
	var result PaginatedResponse
	err := s.client.GET(endpoint, &result)
	return &result, err
}

func (s *WebhooksService) Get(webhookID string) (*Webhook, error) {
	var webhook Webhook
	err := s.client.GET(fmt.Sprintf("webhooks/%s/", webhookID), &webhook)
	return &webhook, err
}

func (s *WebhooksService) Create(url string, events []string, secret string) (*Webhook, error) {
	body := map[string]interface{}{
		"url":    url,
		"events": events,
	}
	if secret != "" {
		body["secret"] = secret
	}
	var result Webhook
	err := s.client.POST("webhooks/", body, &result)
	return &result, err
}

func (s *WebhooksService) Update(webhookID string, webhook *Webhook) (*Webhook, error) {
	var result Webhook
	err := s.client.PATCH(fmt.Sprintf("webhooks/%s/", webhookID), webhook, &result)
	return &result, err
}

func (s *WebhooksService) Delete(webhookID string) error {
	return s.client.DELETE(fmt.Sprintf("webhooks/%s/", webhookID))
}

func (s *WebhooksService) ListEvents(webhookID string, page int) (*PaginatedResponse, error) {
	endpoint := fmt.Sprintf("webhook-logs/?webhook=%s&page=%d", webhookID, page)
	var result PaginatedResponse
	err := s.client.GET(endpoint, &result)
	return &result, err
}

// ============================================================================
// Notifications Service
// ============================================================================

// NotificationsService handles notification-related API calls
type NotificationsService struct {
	client *Client
}

func (s *NotificationsService) List(page int) (*PaginatedResponse, error) {
	endpoint := fmt.Sprintf("notifications/?page=%d", page)
	var result PaginatedResponse
	err := s.client.GET(endpoint, &result)
	return &result, err
}

func (s *NotificationsService) Get(notificationID string) (*Notification, error) {
	var notification Notification
	err := s.client.GET(fmt.Sprintf("notifications/%s/", notificationID), &notification)
	return &notification, err
}

func (s *NotificationsService) MarkAsRead(notificationID string) (*Notification, error) {
	var result Notification
	err := s.client.POST(fmt.Sprintf("notifications/%s/mark-read/", notificationID), nil, &result)
	return &result, err
}

// ============================================================================
// Returns Service
// ============================================================================

// ReturnsService handles return-related API calls
type ReturnsService struct {
	client *Client
}

func (s *ReturnsService) List(page int) (*PaginatedResponse, error) {
	endpoint := fmt.Sprintf("returns/?page=%d", page)
	var result PaginatedResponse
	err := s.client.GET(endpoint, &result)
	return &result, err
}

func (s *ReturnsService) Get(returnID string) (*Return, error) {
	var returnObj Return
	err := s.client.GET(fmt.Sprintf("returns/%s/", returnID), &returnObj)
	return &returnObj, err
}

func (s *ReturnsService) Create(returnObj *Return) (*Return, error) {
	var result Return
	err := s.client.POST("returns/", returnObj, &result)
	return &result, err
}

func (s *ReturnsService) Approve(returnID string) (*Return, error) {
	var result Return
	err := s.client.POST(fmt.Sprintf("returns/%s/approve/", returnID), nil, &result)
	return &result, err
}
