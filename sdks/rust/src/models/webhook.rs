use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Webhook {
    pub id: String,
    pub url: String,
    pub events: Option<Vec<String>>,
    pub is_active: Option<bool>,
    pub secret: String,
    pub created_at: String,
}
