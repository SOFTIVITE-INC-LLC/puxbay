use crate::models::{PaginatedResponse, Product};
use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;
use serde::Serialize;

pub struct ProductsResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> ProductsResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn list(&self, page: i32, page_size: i32) -> Result<PaginatedResponse<Product>, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("products/?page={}&page_size={}", page, page_size),
            None::<()>,
        ).await
    }

    pub async fn get(&self, product_id: &str) -> Result<Product, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("products/{}/", product_id),
            None::<()>,
        ).await
    }

    pub async fn create(&self, product: &Product) -> Result<Product, PuxbayError> {
        self.client.request(
            Method::POST,
            "products/",
            Some(product),
        ).await
    }

    pub async fn update(&self, product_id: &str, product: &Product) -> Result<Product, PuxbayError> {
        self.client.request(
            Method::PATCH,
            &format!("products/{}/", product_id),
            Some(product),
        ).await
    }

    pub async fn delete(&self, product_id: &str) -> Result<(), PuxbayError> {
        self.client.request::<serde_json::Value>(
            Method::DELETE,
            &format!("products/{}/", product_id),
            None::<()>,
        ).await?;
        Ok(())
    }

    pub async fn adjust_stock(&self, product_id: &str, quantity: i32, reason: &str) -> Result<Product, PuxbayError> {
        #[derive(Serialize)]
        struct AdjustStockRequest<'a> {
            quantity: i32,
            reason: &'a str,
        }

        self.client.request(
            Method::POST,
            &format!("products/{}/stock-adjustment/", product_id),
            Some(&AdjustStockRequest { quantity, reason }),
        ).await
    }
}
