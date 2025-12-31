use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Order {
    pub id: String,
    pub order_number: String,
    pub status: String,
    pub subtotal: f64,
    pub tax_amount: f64,
    pub total_amount: f64,
    pub amount_paid: f64,
    pub payment_method: String,
    pub ordering_type: String,
    pub offline_uuid: Option<String>,
    pub customer: Option<String>,
    pub customer_name: Option<String>,
    pub cashier: Option<String>,
    pub cashier_name: Option<String>,
    pub branch: String,
    pub branch_name: String,
    #[serde(default)]
    pub items: Vec<OrderItem>,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct OrderItem {
    pub id: String,
    pub product: String,
    pub product_name: String,
    pub sku: String,
    pub item_number: String,
    pub quantity: i32,
    pub price: f64,
    pub cost_price: Option<f64>,
    pub total_price: f64,
}
