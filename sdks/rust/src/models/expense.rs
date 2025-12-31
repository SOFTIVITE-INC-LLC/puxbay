use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Expense {
    pub id: String,
    pub category: String,
    pub description: String,
    pub amount: f64,
    pub branch: String,
    pub receipt_url: Option<String>,
    pub date: String,
}
