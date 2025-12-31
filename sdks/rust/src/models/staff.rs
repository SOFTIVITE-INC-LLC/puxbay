use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Staff {
    pub id: String,
    pub username: String,
    pub full_name: String,
    pub email: String,
    pub role: String,
    pub branch: Option<String>,
    pub branch_name: Option<String>,
}
