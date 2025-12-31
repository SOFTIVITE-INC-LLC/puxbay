"""Resource module initialization"""

from .products import Products
from .orders import Orders
from .customers import Customers
from .inventory import Inventory
from .reports import Reports
from .categories import Categories
from .suppliers import Suppliers
from .purchase_orders import PurchaseOrders
from .gift_cards import GiftCards
from .expenses import Expenses
from .branches import Branches
from .staff import Staff
from .webhooks import Webhooks

__all__ = [
    "Products",
    "Orders",
    "Customers",
    "Inventory",
    "Reports",
    "Categories",
    "Suppliers",
    "PurchaseOrders",
    "GiftCards",
    "Expenses",
    "Branches",
    "Staff",
    "Webhooks"
]
