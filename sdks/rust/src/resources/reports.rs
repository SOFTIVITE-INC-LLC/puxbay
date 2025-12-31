use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;
use std::collections::HashMap;

pub struct ReportsResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> ReportsResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn financial_summary(&self, start_date: &str, end_date: &str) -> Result<HashMap<String, serde_json::Value>, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("reports/financial-summary/?start_date={}&end_date={}", start_date, end_date),
            None::<()>,
        ).await
    }

    pub async fn daily_sales(&self, start_date: &str, end_date: &str) -> Result<Vec<serde_json::Value>, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("reports/daily-sales/?start_date={}&end_date={}", start_date, end_date),
            None::<()>,
        ).await
    }

    pub async fn top_products(&self, limit: i32) -> Result<Vec<serde_json::Value>, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("reports/top-products/?limit={}", limit),
            None::<()>,
        ).await
    }

    pub async fn low_stock(&self) -> Result<Vec<serde_json::Value>, PuxbayError> {
        self.client.request(
            Method::GET,
            "reports/low-stock/",
            None::<()>,
        ).await
    }
}
