use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Customer {
    pub id: String,
    pub name: String,
    pub email: Option<String>,
    pub phone: Option<String>,
    pub address: Option<String>,
    pub customer_type: String,
    pub loyalty_points: i32,
    pub store_credit_balance: f64,
    pub total_spend: f64,
    pub tier: Option<String>,
    pub tier_name: Option<String>,
    #[serde(default)]
    pub marketing_opt_in: bool,
    pub created_at: String,
}
