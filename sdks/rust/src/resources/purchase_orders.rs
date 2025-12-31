use crate::models::{PaginatedResponse, PurchaseOrder};
use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;
use serde::Serialize;

pub struct PurchaseOrdersResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> PurchaseOrdersResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn list(&self, page: i32, status: Option<&str>) -> Result<PaginatedResponse<PurchaseOrder>, PuxbayError> {
        let mut query = format!("purchase-orders/?page={}", page);
        if let Some(s) = status {
            query.push_str(&format!("&status={}", s));
        }

        self.client.request(
            Method::GET,
            &query,
            None::<()>,
        ).await
    }

    pub async fn get(&self, po_id: &str) -> Result<PurchaseOrder, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("purchase-orders/{}/", po_id),
            None::<()>,
        ).await
    }

    pub async fn create(&self, po: &PurchaseOrder) -> Result<PurchaseOrder, PuxbayError> {
        self.client.request(
            Method::POST,
            "purchase-orders/",
            Some(po),
        ).await
    }

    pub async fn update(&self, po_id: &str, po: &PurchaseOrder) -> Result<PurchaseOrder, PuxbayError> {
        self.client.request(
            Method::PATCH,
            &format!("purchase-orders/{}/", po_id),
            Some(po),
        ).await
    }

    pub async fn receive(&self, po_id: &str, items: Vec<serde_json::Value>) -> Result<PurchaseOrder, PuxbayError> {
        #[derive(Serialize)]
        struct ReceiveRequest {
            items: Vec<serde_json::Value>,
        }

        self.client.request(
            Method::POST,
            &format!("purchase-orders/{}/receive/", po_id),
            Some(&ReceiveRequest { items }),
        ).await
    }
}
