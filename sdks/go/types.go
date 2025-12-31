package puxbay

// Complete type definitions matching the Puxbay API models
import "time"

// ============================================================================
// Core Models
// ============================================================================

type Category struct {
	ID          string `json:"id"`
	Name        string `json:"name"`
	Description string `json:"description,omitempty"`
}

type ProductVariant struct {
	ID            string                 `json:"id"`
	Name          string                 `json:"name"`
	SKU           string                 `json:"sku"`
	Price         float64                `json:"price"`
	StockQuantity int                    `json:"stock_quantity"`
	Attributes    map[string]interface{} `json:"attributes,omitempty"`
	IsActive      bool                   `json:"is_active"`
}

type ProductComponent struct {
	ID               string `json:"id"`
	ComponentProduct string `json:"component_product"`
	ComponentName    string `json:"component_name,omitempty"` // read-only
	ComponentSKU     string `json:"component_sku,omitempty"`  // read-only
	Quantity         int    `json:"quantity"`
}

type ProductHistory struct {
	ID             string `json:"id"`
	Action         string `json:"action"`
	ChangedBy      string `json:"changed_by"`
	ChangedByName  string `json:"changed_by_name,omitempty"` // read-only
	ChangedAt      string `json:"changed_at"`
	ChangesSummary string `json:"changes_summary,omitempty"`
}

type Product struct {
	ID                       string                 `json:"id"`
	Name                     string                 `json:"name"`
	SKU                      string                 `json:"sku"`
	Price                    float64                `json:"price"`
	StockQuantity            int                    `json:"stock_quantity"`
	Description              string                 `json:"description,omitempty"`
	Category                 string                 `json:"category"`
	CategoryName             string                 `json:"category_name,omitempty"` // read-only
	Variants                 []ProductVariant       `json:"variants,omitempty"`      // read-only
	LowStockThreshold        int                    `json:"low_stock_threshold,omitempty"`
	CostPrice                float64                `json:"cost_price,omitempty"`
	ExpiryDate               string                 `json:"expiry_date,omitempty"`
	Barcode                  string                 `json:"barcode,omitempty"`
	IsActive                 bool                   `json:"is_active"`
	MinimumWholesaleQuantity int                    `json:"minimum_wholesale_quantity,omitempty"`
	IsComposite              bool                   `json:"is_composite"`
	Components               []ProductComponent     `json:"components,omitempty"` // read-only
	Metadata                 map[string]interface{} `json:"metadata,omitempty"`
	CreatedAt                time.Time              `json:"created_at"`
	UpdatedAt                time.Time              `json:"updated_at"`
}

type CustomerTier struct {
	ID                 string  `json:"id"`
	Name               string  `json:"name"`
	MinSpend           float64 `json:"min_spend"`
	DiscountPercentage float64 `json:"discount_percentage"`
	Color              string  `json:"color,omitempty"`
	Icon               string  `json:"icon,omitempty"`
}

type Customer struct {
	ID                 string                 `json:"id"`
	Name               string                 `json:"name"`
	Email              string                 `json:"email,omitempty"`
	Phone              string                 `json:"phone,omitempty"`
	Address            string                 `json:"address,omitempty"`
	CustomerType       string                 `json:"customer_type"`
	LoyaltyPoints      int                    `json:"loyalty_points"`
	StoreCreditBalance float64                `json:"store_credit_balance"`
	TotalSpend         float64                `json:"total_spend"`
	Tier               string                 `json:"tier,omitempty"`
	TierName           string                 `json:"tier_name,omitempty"` // read-only
	MarketingOptIn     bool                   `json:"marketing_opt_in"`
	Metadata           map[string]interface{} `json:"metadata,omitempty"`
	CreatedAt          time.Time              `json:"created_at"`
}

type OrderItem struct {
	ID                string  `json:"id"`
	Product           string  `json:"product"`
	ProductName       string  `json:"product_name,omitempty"` // read-only
	SKU               string  `json:"sku,omitempty"`          // read-only
	ItemNumber        string  `json:"item_number,omitempty"`
	Quantity          int     `json:"quantity"`
	Price             float64 `json:"price"`
	CostPrice         float64 `json:"cost_price,omitempty"`
	GetTotalItemPrice float64 `json:"get_total_item_price,omitempty"` // read-only
}

type Order struct {
	ID            string                 `json:"id"`
	OrderNumber   string                 `json:"order_number"`
	Status        string                 `json:"status"`
	CreatedAt     time.Time              `json:"created_at"`
	UpdatedAt     time.Time              `json:"updated_at"`
	Subtotal      float64                `json:"subtotal"`
	TaxAmount     float64                `json:"tax_amount"`
	TotalAmount   float64                `json:"total_amount"`
	AmountPaid    float64                `json:"amount_paid"`
	PaymentMethod string                 `json:"payment_method"`
	OrderingType  string                 `json:"ordering_type"`
	OfflineUUID   string                 `json:"offline_uuid,omitempty"`
	Customer      string                 `json:"customer,omitempty"`
	CustomerName  string                 `json:"customer_name,omitempty"` // read-only
	Cashier       string                 `json:"cashier,omitempty"`
	CashierName   string                 `json:"cashier_name,omitempty"` // read-only
	Branch        string                 `json:"branch,omitempty"`
	BranchName    string                 `json:"branch_name,omitempty"` // read-only
	Items         []OrderItem            `json:"items,omitempty"`       // read-only
	Metadata      map[string]interface{} `json:"metadata,omitempty"`
}

// ============================================================================
// Supply Chain Models
// ============================================================================

type Supplier struct {
	ID            string    `json:"id"`
	Name          string    `json:"name"`
	ContactPerson string    `json:"contact_person,omitempty"`
	Email         string    `json:"email,omitempty"`
	Phone         string    `json:"phone,omitempty"`
	Address       string    `json:"address,omitempty"`
	CreatedAt     time.Time `json:"created_at"`
}

type PurchaseOrderItem struct {
	ID          string  `json:"id"`
	Product     string  `json:"product"`
	ProductName string  `json:"product_name,omitempty"` // read-only
	SKU         string  `json:"sku,omitempty"`          // read-only
	Quantity    int     `json:"quantity"`
	UnitCost    float64 `json:"unit_cost"`
}

type PurchaseOrder struct {
	ID            string              `json:"id"`
	ReferenceID   string              `json:"reference_id"`
	Status        string              `json:"status"`
	Supplier      string              `json:"supplier"`
	SupplierName  string              `json:"supplier_name,omitempty"` // read-only
	Branch        string              `json:"branch"`
	BranchName    string              `json:"branch_name,omitempty"` // read-only
	TotalCost     float64             `json:"total_cost"`
	ExpectedDate  string              `json:"expected_date,omitempty"`
	Notes         string              `json:"notes,omitempty"`
	CreatedBy     string              `json:"created_by"`
	CreatedByName string              `json:"created_by_name,omitempty"` // read-only
	CreatedAt     time.Time           `json:"created_at"`
	Items         []PurchaseOrderItem `json:"items,omitempty"` // read-only
}

type StockTransferItem struct {
	ID            string  `json:"id"`
	Product       string  `json:"product"`
	ProductName   string  `json:"product_name,omitempty"` // read-only
	Quantity      int     `json:"quantity"`
	TransferPrice float64 `json:"transfer_price,omitempty"`
}

type StockTransfer struct {
	ID                    string              `json:"id"`
	ReferenceID           string              `json:"reference_id"`
	Status                string              `json:"status"`
	SourceBranch          string              `json:"source_branch"`
	SourceBranchName      string              `json:"source_branch_name,omitempty"` // read-only
	DestinationBranch     string              `json:"destination_branch"`
	DestinationBranchName string              `json:"destination_branch_name,omitempty"` // read-only
	Notes                 string              `json:"notes,omitempty"`
	CreatedBy             string              `json:"created_by"`
	CreatedByName         string              `json:"created_by_name,omitempty"` // read-only
	CreatedAt             time.Time           `json:"created_at"`
	CompletedAt           *time.Time          `json:"completed_at,omitempty"`
	Items                 []StockTransferItem `json:"items,omitempty"` // read-only
}

// ============================================================================
// Store Operations Models
// ============================================================================

type StocktakeEntry struct {
	ID               string    `json:"id"`
	Product          string    `json:"product"`
	ProductName      string    `json:"product_name,omitempty"` // read-only
	SKU              string    `json:"sku,omitempty"`          // read-only
	CountedQuantity  int       `json:"counted_quantity"`
	ExpectedQuantity int       `json:"expected_quantity"`
	Difference       int       `json:"difference,omitempty"` // read-only
	Notes            string    `json:"notes,omitempty"`
	UpdatedAt        time.Time `json:"updated_at"`
}

type StocktakeSession struct {
	ID            string           `json:"id"`
	Branch        string           `json:"branch"`
	BranchName    string           `json:"branch_name,omitempty"` // read-only
	Status        string           `json:"status"`
	Notes         string           `json:"notes,omitempty"`
	CreatedBy     string           `json:"created_by"`
	CreatedByName string           `json:"created_by_name,omitempty"` // read-only
	StartedAt     time.Time        `json:"started_at"`
	CompletedAt   *time.Time       `json:"completed_at,omitempty"`
	Entries       []StocktakeEntry `json:"entries,omitempty"` // read-only
}

type CashDrawerSession struct {
	ID              string     `json:"id"`
	Branch          string     `json:"branch"`
	BranchName      string     `json:"branch_name,omitempty"` // read-only
	Employee        string     `json:"employee"`
	EmployeeName    string     `json:"employee_name,omitempty"` // read-only
	Status          string     `json:"status"`
	StartTime       time.Time  `json:"start_time"`
	EndTime         *time.Time `json:"end_time,omitempty"`
	StartingBalance float64    `json:"starting_balance"`
	ExpectedCash    float64    `json:"expected_cash,omitempty"`
	ActualCash      float64    `json:"actual_cash,omitempty"`
	Difference      float64    `json:"difference,omitempty"`
	Notes           string     `json:"notes,omitempty"`
}

// ============================================================================
// Notifications & CRM Models
// ============================================================================

type Notification struct {
	ID               string    `json:"id"`
	Title            string    `json:"title"`
	Message          string    `json:"message"`
	NotificationType string    `json:"notification_type"`
	Category         string    `json:"category"`
	IsRead           bool      `json:"is_read"`
	CreatedAt        time.Time `json:"created_at"`
}

type CustomerFeedback struct {
	ID           string    `json:"id"`
	Customer     string    `json:"customer"`
	CustomerName string    `json:"customer_name,omitempty"` // read-only
	Transaction  string    `json:"transaction,omitempty"`
	Rating       int       `json:"rating"`
	Comment      string    `json:"comment,omitempty"`
	CreatedAt    time.Time `json:"created_at"`
}

type GiftCard struct {
	ID         string  `json:"id"`
	Code       string  `json:"code"`
	Balance    float64 `json:"balance"`
	Status     string  `json:"status"`
	ExpiryDate string  `json:"expiry_date,omitempty"`
}

type LoyaltyTransaction struct {
	ID              string    `json:"id"`
	Customer        string    `json:"customer"`
	Order           string    `json:"order,omitempty"`
	Points          int       `json:"points"`
	TransactionType string    `json:"transaction_type"`
	Description     string    `json:"description,omitempty"`
	CreatedAt       time.Time `json:"created_at"`
}

type StoreCreditTransaction struct {
	ID        string    `json:"id"`
	Customer  string    `json:"customer"`
	Amount    float64   `json:"amount"`
	Reference string    `json:"reference,omitempty"`
	CreatedAt time.Time `json:"created_at"`
}

// ============================================================================
// Returns & Financial Models
// ============================================================================

type ReturnItem struct {
	ID          string  `json:"id"`
	Product     string  `json:"product"`
	ProductName string  `json:"product_name,omitempty"` // read-only
	Quantity    int     `json:"quantity"`
	Condition   string  `json:"condition"`
	Restock     bool    `json:"restock"`
	UnitPrice   float64 `json:"unit_price"`
}

type Return struct {
	ID           string       `json:"id"`
	Order        string       `json:"order"`
	OrderNumber  string       `json:"order_number,omitempty"` // read-only
	Customer     string       `json:"customer,omitempty"`
	CustomerName string       `json:"customer_name,omitempty"` // read-only
	Reason       string       `json:"reason"`
	ReasonDetail string       `json:"reason_detail,omitempty"`
	Status       string       `json:"status"`
	RefundMethod string       `json:"refund_method"`
	RefundAmount float64      `json:"refund_amount"`
	CreatedAt    time.Time    `json:"created_at"`
	Items        []ReturnItem `json:"items,omitempty"` // read-only
}

type ExpenseCategory struct {
	ID   string `json:"id"`
	Name string `json:"name"`
	Type string `json:"type"`
}

type Expense struct {
	ID            string    `json:"id"`
	Category      string    `json:"category"`
	CategoryName  string    `json:"category_name,omitempty"` // read-only
	Amount        float64   `json:"amount"`
	Date          string    `json:"date"`
	Description   string    `json:"description,omitempty"`
	ReceiptFile   string    `json:"receipt_file,omitempty"`
	CreatedBy     string    `json:"created_by"`
	CreatedByName string    `json:"created_by_name,omitempty"` // read-only
	CreatedAt     time.Time `json:"created_at"`
}

type PaymentMethod struct {
	ID       string `json:"id"`
	Name     string `json:"name"`
	Provider string `json:"provider,omitempty"`
	IsActive bool   `json:"is_active"`
}

type Branch struct {
	ID                string    `json:"id"`
	Name              string    `json:"name"`
	UniqueID          string    `json:"unique_id"`
	Address           string    `json:"address,omitempty"`
	Phone             string    `json:"phone,omitempty"`
	BranchType        string    `json:"branch_type"`
	CurrencyCode      string    `json:"currency_code"`
	CurrencySymbol    string    `json:"currency_symbol"`
	LowStockThreshold int       `json:"low_stock_threshold"`
	CreatedAt         time.Time `json:"created_at"`
	UpdatedAt         time.Time `json:"updated_at"`
}

type TaxConfiguration struct {
	ID                 string    `json:"id"`
	TaxType            string    `json:"tax_type"`
	TaxRate            float64   `json:"tax_rate"`
	TaxNumber          string    `json:"tax_number,omitempty"`
	IncludeTaxInPrices bool      `json:"include_tax_in_prices"`
	IsActive           bool      `json:"is_active"`
	UpdatedAt          time.Time `json:"updated_at"`
}

type StaffMember struct {
	ID         string `json:"id"`
	Username   string `json:"username,omitempty"`  // read-only
	FullName   string `json:"full_name,omitempty"` // read-only
	Email      string `json:"email,omitempty"`     // read-only
	Role       string `json:"role"`
	Branch     string `json:"branch,omitempty"`
	BranchName string `json:"branch_name,omitempty"` // read-only
}

// ============================================================================
// Webhook Models
// ============================================================================

type Webhook struct {
	ID        string    `json:"id"`
	URL       string    `json:"url"`
	Events    []string  `json:"events"`
	IsActive  bool      `json:"is_active"`
	Secret    string    `json:"secret,omitempty"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type WebhookEvent struct {
	ID         string      `json:"id"`
	Webhook    string      `json:"webhook"`
	EventType  string      `json:"event_type"`
	Payload    interface{} `json:"payload"`
	StatusCode int         `json:"status_code,omitempty"`
	Response   string      `json:"response,omitempty"`
	CreatedAt  time.Time   `json:"created_at"`
}
