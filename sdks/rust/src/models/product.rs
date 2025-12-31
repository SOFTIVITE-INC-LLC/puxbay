use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Product {
    pub id: String,
    pub name: String,
    pub sku: String,
    pub price: f64,
    pub stock_quantity: i32,
    pub description: Option<String>,
    pub category: Option<String>,
    pub category_name: Option<String>,
    #[serde(default = "default_true")]
    pub is_active: bool,
    pub low_stock_threshold: Option<i32>,
    pub cost_price: Option<f64>,
    pub barcode: Option<String>,
    #[serde(default)]
    pub is_composite: bool,
    pub created_at: Option<String>,
    pub updated_at: Option<String>,
}

fn default_true() -> bool {
    true
}
