use crate::models::{PaginatedResponse, StockTransfer};
use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;

pub struct StockTransfersResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> StockTransfersResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn list(&self, page: i32, status: Option<&str>) -> Result<PaginatedResponse<StockTransfer>, PuxbayError> {
        let mut query = format!("stock-transfers/?page={}", page);
        if let Some(s) = status {
            query.push_str(&format!("&status={}", s));
        }

        self.client.request(
            Method::GET,
            &query,
            None::<()>,
        ).await
    }

    pub async fn get(&self, transfer_id: &str) -> Result<StockTransfer, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("stock-transfers/{}/", transfer_id),
            None::<()>,
        ).await
    }

    pub async fn create(&self, transfer: &StockTransfer) -> Result<StockTransfer, PuxbayError> {
        self.client.request(
            Method::POST,
            "stock-transfers/",
            Some(transfer),
        ).await
    }

    pub async fn complete(&self, transfer_id: &str) -> Result<StockTransfer, PuxbayError> {
        self.client.request(
            Method::POST,
            &format!("stock-transfers/{}/complete/", transfer_id),
            None::<()>,
        ).await
    }
}
