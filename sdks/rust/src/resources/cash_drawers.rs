use crate::models::{PaginatedResponse, CashDrawerSession};
use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;
use serde::Serialize;
use std::collections::HashMap;

pub struct CashDrawersResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> CashDrawersResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn list(&self, page: i32) -> Result<PaginatedResponse<CashDrawerSession>, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("cash-drawers/?page={}", page),
            None::<()>,
        ).await
    }

    pub async fn get(&self, drawer_id: &str) -> Result<CashDrawerSession, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("cash-drawers/{}/", drawer_id),
            None::<()>,
        ).await
    }

    pub async fn open(&self, drawer_data: HashMap<String, serde_json::Value>) -> Result<CashDrawerSession, PuxbayError> {
        self.client.request(
            Method::POST,
            "cash-drawers/",
            Some(&drawer_data),
        ).await
    }

    pub async fn close(&self, drawer_id: &str, actual_cash: f64) -> Result<CashDrawerSession, PuxbayError> {
        #[derive(Serialize)]
        struct CloseRequest {
            actual_cash: f64,
        }

        self.client.request(
            Method::POST,
            &format!("cash-drawers/{}/close/", drawer_id),
            Some(&CloseRequest { actual_cash }),
        ).await
    }
}
