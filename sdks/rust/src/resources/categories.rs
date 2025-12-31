use crate::models::{PaginatedResponse, Category};
use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;

pub struct CategoriesResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> CategoriesResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn list(&self, page: i32) -> Result<PaginatedResponse<Category>, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("categories/?page={}", page),
            None::<()>,
        ).await
    }

    pub async fn get(&self, category_id: &str) -> Result<Category, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("categories/{}/", category_id),
            None::<()>,
        ).await
    }

    pub async fn create(&self, category: &Category) -> Result<Category, PuxbayError> {
        self.client.request(
            Method::POST,
            "categories/",
            Some(category),
        ).await
    }

    pub async fn update(&self, category_id: &str, category: &Category) -> Result<Category, PuxbayError> {
        self.client.request(
            Method::PATCH,
            &format!("categories/{}/", category_id),
            Some(category),
        ).await
    }

    pub async fn delete(&self, category_id: &str) -> Result<(), PuxbayError> {
        self.client.request::<serde_json::Value>(
            Method::DELETE,
            &format!("categories/{}/", category_id),
            None::<()>,
        ).await?;
        Ok(())
    }
}
