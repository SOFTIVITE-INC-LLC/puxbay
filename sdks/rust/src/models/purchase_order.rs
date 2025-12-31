use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct PurchaseOrder {
    pub id: String,
    pub po_number: String,
    pub supplier: String,
    pub supplier_name: Option<String>,
    pub status: String,
    pub total_amount: f64,
    pub expected_delivery_date: Option<String>,
    // Simplified items for now, ideally strictly typed POItem
    pub items: Option<Vec<serde_json::Value>>, 
    pub created_at: String,
    pub updated_at: String,
}
