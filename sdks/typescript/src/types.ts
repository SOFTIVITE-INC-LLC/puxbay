// Complete type definitions matching the Puxbay API models

export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

export interface ListParams {
    page?: number;
    page_size?: number;
    search?: string;
}

export interface OrderListParams extends ListParams {
    status?: string;
    customer?: string;
    payment_method?: string;
    ordering_type?: string;
}

// ============================================================================
// Core Models
// ============================================================================

export interface Category {
    id: string;
    name: string;
    description?: string;
}

export interface ProductVariant {
    id: string;
    name: string;
    sku: string;
    price: number;
    stock_quantity: number;
    attributes?: Record<string, any>;
    is_active: boolean;
}

export interface ProductComponent {
    id: string;
    component_product: string;
    component_name?: string; // read-only
    component_sku?: string; // read-only
    quantity: number;
}

export interface ProductHistory {
    id: string;
    action: string;
    changed_by: string;
    changed_by_name?: string; // read-only
    changed_at: string;
    changes_summary?: string;
}

export interface Product {
    id: string;
    name: string;
    sku: string;
    price: number;
    stock_quantity: number;
    description?: string;
    category: string;
    category_name?: string; // read-only
    variants?: ProductVariant[]; // read-only
    low_stock_threshold?: number;
    cost_price?: number;
    expiry_date?: string;
    barcode?: string;
    is_active: boolean;
    minimum_wholesale_quantity?: number;
    is_composite: boolean;
    components?: ProductComponent[]; // read-only
    metadata?: Record<string, any>;
    created_at: string;
    updated_at: string;
}

export interface CustomerTier {
    id: string;
    name: string;
    min_spend: number;
    discount_percentage: number;
    color?: string;
    icon?: string;
}

export interface Customer {
    id: string;
    name: string;
    email?: string;
    phone?: string;
    address?: string;
    customer_type: string;
    loyalty_points: number;
    store_credit_balance: number;
    total_spend: number;
    tier?: string;
    tier_name?: string; // read-only
    marketing_opt_in: boolean;
    metadata?: Record<string, any>;
    created_at: string;
}

export interface OrderItem {
    id: string;
    product: string;
    product_name?: string; // read-only
    sku?: string; // read-only
    item_number?: string;
    quantity: number;
    price: number;
    cost_price?: number;
    get_total_item_price?: number; // read-only
}

export interface Order {
    id: string;
    order_number: string;
    status: string;
    created_at: string;
    updated_at: string;
    subtotal: number;
    tax_amount: number;
    total_amount: number;
    amount_paid: number;
    payment_method: string;
    ordering_type: string;
    offline_uuid?: string;
    customer?: string;
    customer_name?: string; // read-only
    cashier?: string;
    cashier_name?: string; // read-only
    branch?: string;
    branch_name?: string; // read-only
    items?: OrderItem[]; // read-only
    metadata?: Record<string, any>;
}

// ============================================================================
// Supply Chain Models
// ============================================================================

export interface Supplier {
    id: string;
    name: string;
    contact_person?: string;
    email?: string;
    phone?: string;
    address?: string;
    created_at: string;
}

export interface PurchaseOrderItem {
    id: string;
    product: string;
    product_name?: string; // read-only
    sku?: string; // read-only
    quantity: number;
    unit_cost: number;
}

export interface PurchaseOrder {
    id: string;
    reference_id: string;
    status: string;
    supplier: string;
    supplier_name?: string; // read-only
    branch: string;
    branch_name?: string; // read-only
    total_cost: number;
    expected_date?: string;
    notes?: string;
    created_by: string;
    created_by_name?: string; // read-only
    created_at: string;
    items?: PurchaseOrderItem[]; // read-only
}

export interface StockTransferItem {
    id: string;
    product: string;
    product_name?: string; // read-only
    quantity: number;
    transfer_price?: number;
}

export interface StockTransfer {
    id: string;
    reference_id: string;
    status: string;
    source_branch: string;
    source_branch_name?: string; // read-only
    destination_branch: string;
    destination_branch_name?: string; // read-only
    notes?: string;
    created_by: string;
    created_by_name?: string; // read-only
    created_at: string;
    completed_at?: string;
    items?: StockTransferItem[]; // read-only
}

// ============================================================================
// Store Operations Models
// ============================================================================

export interface StocktakeEntry {
    id: string;
    product: string;
    product_name?: string; // read-only
    sku?: string; // read-only
    counted_quantity: number;
    expected_quantity: number;
    difference?: number; // read-only
    notes?: string;
    updated_at: string;
}

export interface StocktakeSession {
    id: string;
    branch: string;
    branch_name?: string; // read-only
    status: string;
    notes?: string;
    created_by: string;
    created_by_name?: string; // read-only
    started_at: string;
    completed_at?: string;
    entries?: StocktakeEntry[]; // read-only
}

export interface CashDrawerSession {
    id: string;
    branch: string;
    branch_name?: string; // read-only
    employee: string;
    employee_name?: string; // read-only
    status: string;
    start_time: string;
    end_time?: string;
    starting_balance: number;
    expected_cash?: number;
    actual_cash?: number;
    difference?: number;
    notes?: string;
}

// ============================================================================
// Notifications & CRM Models
// ============================================================================

export interface Notification {
    id: string;
    title: string;
    message: string;
    notification_type: string;
    category: string;
    is_read: boolean;
    created_at: string;
}

export interface CustomerFeedback {
    id: string;
    customer: string;
    customer_name?: string; // read-only
    transaction?: string;
    rating: number;
    comment?: string;
    created_at: string;
}

export interface GiftCard {
    id: string;
    code: string;
    balance: number;
    status: string;
    expiry_date?: string;
}

export interface LoyaltyTransaction {
    id: string;
    customer: string;
    order?: string;
    points: number;
    transaction_type: string;
    description?: string;
    created_at: string;
}

export interface StoreCreditTransaction {
    id: string;
    customer: string;
    amount: number;
    reference?: string;
    created_at: string;
}

// ============================================================================
// Returns & Financial Models
// ============================================================================

export interface ReturnItem {
    id: string;
    product: string;
    product_name?: string; // read-only
    quantity: number;
    condition: string;
    restock: boolean;
    unit_price: number;
}

export interface Return {
    id: string;
    order: string;
    order_number?: string; // read-only
    customer?: string;
    customer_name?: string; // read-only
    reason: string;
    reason_detail?: string;
    status: string;
    refund_method: string;
    refund_amount: number;
    created_at: string;
    items?: ReturnItem[]; // read-only
}

export interface ExpenseCategory {
    id: string;
    name: string;
    type: string;
}

export interface Expense {
    id: string;
    category: string;
    category_name?: string; // read-only
    amount: number;
    date: string;
    description?: string;
    receipt_file?: string;
    created_by: string;
    created_by_name?: string; // read-only
    created_at: string;
}

export interface PaymentMethod {
    id: string;
    name: string;
    provider?: string;
    is_active: boolean;
}

export interface Branch {
    id: string;
    name: string;
    unique_id: string;
    address?: string;
    phone?: string;
    branch_type: string;
    currency_code: string;
    currency_symbol: string;
    low_stock_threshold: number;
    created_at: string;
    updated_at: string;
}

export interface TaxConfiguration {
    id: string;
    tax_type: string;
    tax_rate: number;
    tax_number?: string;
    include_tax_in_prices: boolean;
    is_active: boolean;
    updated_at: string;
}

export interface Staff {
    id: string;
    username?: string; // read-only
    full_name?: string; // read-only
    email?: string; // read-only
    role: string;
    branch?: string;
    branch_name?: string; // read-only
}

// ============================================================================
// Webhook Models
// ============================================================================

export interface Webhook {
    id: string;
    url: string;
    events: string[];
    is_active: boolean;
    secret?: string;
    created_at: string;
    updated_at: string;
}

export interface WebhookEvent {
    id: string;
    webhook: string;
    event_type: string;
    payload: any;
    status_code?: number;
    response?: string;
    created_at: string;
}

// ============================================================================
// Report Models
// ============================================================================

export interface FinancialSummary {
    total_sales: number;
    total_orders: number;
    average_order_value: number;
    total_expenses: number;
    net_profit: number;
    top_products: Product[];
}

export interface DailySales {
    date: string;
    total_sales: number;
    order_count: number;
}

export interface SalesSummary {
    total_sales: number;
    total_orders: number;
    average_order: number;
    top_products: Product[];
}

export interface CustomerAnalytics {
    new_customers: number;
    retention_rate: number;
    average_lifetime_value: number;
}

export interface ProfitLoss {
    revenue: number;
    costs: number;
    gross_profit: number;
    net_profit: number;
}

export interface StockLevel {
    product_id: string;
    product_name: string;
    quantity: number;
    branch: string;
}
