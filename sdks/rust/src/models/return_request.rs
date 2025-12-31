use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct ReturnRequest {
    pub id: String,
    pub order: String,
    pub status: String,
    pub reason: String,
    pub refund_amount: f64,
    pub created_at: String,
    pub updated_at: String,
}
