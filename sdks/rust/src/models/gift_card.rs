use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct GiftCard {
    pub id: String,
    pub code: String,
    pub balance: f64,
    pub status: String,
    pub expiry_date: Option<String>,
}
