"""
Type definitions for Puxbay API models using TypedDict for better IDE support
"""

from typing import TypedDict, List, Optional, Any, Dict
from datetime import datetime


class PaginatedResponse(TypedDict, total=False):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[Any]


# ============================================================================
# Core Models
# ============================================================================

class Category(TypedDict, total=False):
    id: str
    name: str
    description: Optional[str]


class ProductVariant(TypedDict, total=False):
    id: str
    name: str
    sku: str
    price: float
    stock_quantity: int
    attributes: Optional[Dict[str, Any]]
    is_active: bool


class ProductComponent(TypedDict, total=False):
    id: str
    component_product: str
    component_name: Optional[str]  # read-only
    component_sku: Optional[str]  # read-only
    quantity: int


class ProductHistory(TypedDict, total=False):
    id: str
    action: str
    changed_by: str
    changed_by_name: Optional[str]  # read-only
    changed_at: str
    changes_summary: Optional[str]


class Product(TypedDict, total=False):
    id: str
    name: str
    sku: str
    price: float
    stock_quantity: int
    description: Optional[str]
    category: str
    category_name: Optional[str]  # read-only
    variants: Optional[List[ProductVariant]]  # read-only
    low_stock_threshold: Optional[int]
    cost_price: Optional[float]
    expiry_date: Optional[str]
    barcode: Optional[str]
    is_active: bool
    minimum_wholesale_quantity: Optional[int]
    is_composite: bool
    components: Optional[List[ProductComponent]]  # read-only
    metadata: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class CustomerTier(TypedDict, total=False):
    id: str
    name: str
    min_spend: float
    discount_percentage: float
    color: Optional[str]
    icon: Optional[str]


class Customer(TypedDict, total=False):
    id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    customer_type: str
    loyalty_points: int
    store_credit_balance: float
    total_spend: float
    tier: Optional[str]
    tier_name: Optional[str]  # read-only
    marketing_opt_in: bool
    metadata: Optional[Dict[str, Any]]
    created_at: str


class OrderItem(TypedDict, total=False):
    id: str
    product: str
    product_name: Optional[str]  # read-only
    sku: Optional[str]  # read-only
    item_number: Optional[str]
    quantity: int
    price: float
    cost_price: Optional[float]
    get_total_item_price: Optional[float]  # read-only


class Order(TypedDict, total=False):
    id: str
    order_number: str
    status: str
    created_at: str
    updated_at: str
    subtotal: float
    tax_amount: float
    total_amount: float
    amount_paid: float
    payment_method: str
    ordering_type: str
    offline_uuid: Optional[str]
    customer: Optional[str]
    customer_name: Optional[str]  # read-only
    cashier: Optional[str]
    cashier_name: Optional[str]  # read-only
    branch: Optional[str]
    branch_name: Optional[str]  # read-only
    items: Optional[List[OrderItem]]  # read-only
    metadata: Optional[Dict[str, Any]]


# ============================================================================
# Supply Chain Models
# ============================================================================

class Supplier(TypedDict, total=False):
    id: str
    name: str
    contact_person: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    created_at: str


class PurchaseOrderItem(TypedDict, total=False):
    id: str
    product: str
    product_name: Optional[str]  # read-only
    sku: Optional[str]  # read-only
    quantity: int
    unit_cost: float


class PurchaseOrder(TypedDict, total=False):
    id: str
    reference_id: str
    status: str
    supplier: str
    supplier_name: Optional[str]  # read-only
    branch: str
    branch_name: Optional[str]  # read-only
    total_cost: float
    expected_date: Optional[str]
    notes: Optional[str]
    created_by: str
    created_by_name: Optional[str]  # read-only
    created_at: str
    items: Optional[List[PurchaseOrderItem]]  # read-only


class StockTransferItem(TypedDict, total=False):
    id: str
    product: str
    product_name: Optional[str]  # read-only
    quantity: int
    transfer_price: Optional[float]


class StockTransfer(TypedDict, total=False):
    id: str
    reference_id: str
    status: str
    source_branch: str
    source_branch_name: Optional[str]  # read-only
    destination_branch: str
    destination_branch_name: Optional[str]  # read-only
    notes: Optional[str]
    created_by: str
    created_by_name: Optional[str]  # read-only
    created_at: str
    completed_at: Optional[str]
    items: Optional[List[StockTransferItem]]  # read-only


# ============================================================================
# Store Operations Models
# ============================================================================

class StocktakeEntry(TypedDict, total=False):
    id: str
    product: str
    product_name: Optional[str]  # read-only
    sku: Optional[str]  # read-only
    counted_quantity: int
    expected_quantity: int
    difference: Optional[int]  # read-only
    notes: Optional[str]
    updated_at: str


class StocktakeSession(TypedDict, total=False):
    id: str
    branch: str
    branch_name: Optional[str]  # read-only
    status: str
    notes: Optional[str]
    created_by: str
    created_by_name: Optional[str]  # read-only
    started_at: str
    completed_at: Optional[str]
    entries: Optional[List[StocktakeEntry]]  # read-only


class CashDrawerSession(TypedDict, total=False):
    id: str
    branch: str
    branch_name: Optional[str]  # read-only
    employee: str
    employee_name: Optional[str]  # read-only
    status: str
    start_time: str
    end_time: Optional[str]
    starting_balance: float
    expected_cash: Optional[float]
    actual_cash: Optional[float]
    difference: Optional[float]
    notes: Optional[str]


# ============================================================================
# Notifications & CRM Models
# ============================================================================

class Notification(TypedDict, total=False):
    id: str
    title: str
    message: str
    notification_type: str
    category: str
    is_read: bool
    created_at: str


class CustomerFeedback(TypedDict, total=False):
    id: str
    customer: str
    customer_name: Optional[str]  # read-only
    transaction: Optional[str]
    rating: int
    comment: Optional[str]
    created_at: str


class GiftCard(TypedDict, total=False):
    id: str
    code: str
    balance: float
    status: str
    expiry_date: Optional[str]


class LoyaltyTransaction(TypedDict, total=False):
    id: str
    customer: str
    order: Optional[str]
    points: int
    transaction_type: str
    description: Optional[str]
    created_at: str


class StoreCreditTransaction(TypedDict, total=False):
    id: str
    customer: str
    amount: float
    reference: Optional[str]
    created_at: str


# ============================================================================
# Returns & Financial Models
# ============================================================================

class ReturnItem(TypedDict, total=False):
    id: str
    product: str
    product_name: Optional[str]  # read-only
    quantity: int
    condition: str
    restock: bool
    unit_price: float


class Return(TypedDict, total=False):
    id: str
    order: str
    order_number: Optional[str]  # read-only
    customer: Optional[str]
    customer_name: Optional[str]  # read-only
    reason: str
    reason_detail: Optional[str]
    status: str
    refund_method: str
    refund_amount: float
    created_at: str
    items: Optional[List[ReturnItem]]  # read-only


class ExpenseCategory(TypedDict, total=False):
    id: str
    name: str
    type: str


class Expense(TypedDict, total=False):
    id: str
    category: str
    category_name: Optional[str]  # read-only
    amount: float
    date: str
    description: Optional[str]
    receipt_file: Optional[str]
    created_by: str
    created_by_name: Optional[str]  # read-only
    created_at: str


class PaymentMethod(TypedDict, total=False):
    id: str
    name: str
    provider: Optional[str]
    is_active: bool


class Branch(TypedDict, total=False):
    id: str
    name: str
    unique_id: str
    address: Optional[str]
    phone: Optional[str]
    branch_type: str
    currency_code: str
    currency_symbol: str
    low_stock_threshold: int
    created_at: str
    updated_at: str


class TaxConfiguration(TypedDict, total=False):
    id: str
    tax_type: str
    tax_rate: float
    tax_number: Optional[str]
    include_tax_in_prices: bool
    is_active: bool
    updated_at: str


class Staff(TypedDict, total=False):
    id: str
    username: Optional[str]  # read-only
    full_name: Optional[str]  # read-only
    email: Optional[str]  # read-only
    role: str
    branch: Optional[str]
    branch_name: Optional[str]  # read-only


# ============================================================================
# Webhook Models
# ============================================================================

class Webhook(TypedDict, total=False):
    id: str
    url: str
    events: List[str]
    is_active: bool
    secret: Optional[str]
    created_at: str
    updated_at: str


class WebhookEvent(TypedDict, total=False):
    id: str
    webhook: str
    event_type: str
    payload: Any
    status_code: Optional[int]
    response: Optional[str]
    created_at: str
