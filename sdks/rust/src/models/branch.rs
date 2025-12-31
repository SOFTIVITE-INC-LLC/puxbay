use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Branch {
    pub id: String,
    pub name: String,
    pub unique_id: String,
    pub address: Option<String>,
    pub phone: Option<String>,
    pub branch_type: String,
    pub currency_code: String,
    pub currency_symbol: String,
    pub low_stock_threshold: i32,
    pub created_at: String,
    pub updated_at: String,
}
