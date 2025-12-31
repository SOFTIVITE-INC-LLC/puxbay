use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct StockTransfer {
    pub id: String,
    pub source_branch: String,
    pub source_branch_name: Option<String>,
    pub destination_branch: String,
    pub destination_branch_name: Option<String>,
    pub status: String,
    pub items: Option<Vec<serde_json::Value>>,
    pub notes: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}
