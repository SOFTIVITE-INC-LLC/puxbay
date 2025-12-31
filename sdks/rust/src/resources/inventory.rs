use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;
use serde::Deserialize;

pub struct InventoryResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> InventoryResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn get_stock_levels(&self, branch_id: &str) -> Result<Vec<serde_json::Value>, PuxbayError> {
        #[derive(Deserialize)]
        struct Response {
            results: Vec<serde_json::Value>,
        }
        
        let response: Response = self.client.request(
            Method::GET,
            &format!("inventory/stock-levels/?branch={}", branch_id),
            None::<()>,
        ).await?;
        
        Ok(response.results)
    }

    pub async fn get_product_stock(&self, product_id: &str, branch_id: &str) -> Result<serde_json::Value, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("inventory/product-stock/?product={}&branch={}", product_id, branch_id),
            None::<()>,
        ).await
    }
}
