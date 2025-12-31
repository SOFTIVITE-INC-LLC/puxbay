use crate::models::{PaginatedResponse, Supplier};
use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;

pub struct SuppliersResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> SuppliersResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn list(&self, page: i32, page_size: i32) -> Result<PaginatedResponse<Supplier>, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("suppliers/?page={}&page_size={}", page, page_size),
            None::<()>,
        ).await
    }

    pub async fn get(&self, supplier_id: &str) -> Result<Supplier, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("suppliers/{}/", supplier_id),
            None::<()>,
        ).await
    }

    pub async fn create(&self, supplier: &Supplier) -> Result<Supplier, PuxbayError> {
        self.client.request(
            Method::POST,
            "suppliers/",
            Some(supplier),
        ).await
    }

    pub async fn update(&self, supplier_id: &str, supplier: &Supplier) -> Result<Supplier, PuxbayError> {
        self.client.request(
            Method::PATCH,
            &format!("suppliers/{}/", supplier_id),
            Some(supplier),
        ).await
    }

    pub async fn delete(&self, supplier_id: &str) -> Result<(), PuxbayError> {
        self.client.request::<serde_json::Value>(
            Method::DELETE,
            &format!("suppliers/{}/", supplier_id),
            None::<()>,
        ).await?;
        Ok(())
    }
}
