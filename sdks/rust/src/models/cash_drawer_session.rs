use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct CashDrawerSession {
    pub id: String,
    pub branch: String,
    pub opened_by: String,
    pub closed_by: Option<String>,
    pub opening_cash: f64,
    pub closing_cash: Option<f64>,
    pub actual_cash: Option<f64>,
    pub status: String,
    pub opened_at: String,
    pub closed_at: Option<String>,
}
