use crate::models::{PaginatedResponse, Branch};
use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;

pub struct BranchesResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> BranchesResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn list(&self, page: i32) -> Result<PaginatedResponse<Branch>, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("branches/?page={}", page),
            None::<()>,
        ).await
    }

    pub async fn get(&self, branch_id: &str) -> Result<Branch, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("branches/{}/", branch_id),
            None::<()>,
        ).await
    }

    pub async fn create(&self, branch: &Branch) -> Result<Branch, PuxbayError> {
        self.client.request(
            Method::POST,
            "branches/",
            Some(branch),
        ).await
    }

    pub async fn update(&self, branch_id: &str, branch: &Branch) -> Result<Branch, PuxbayError> {
        self.client.request(
            Method::PATCH,
            &format!("branches/{}/", branch_id),
            Some(branch),
        ).await
    }

    pub async fn delete(&self, branch_id: &str) -> Result<(), PuxbayError> {
        self.client.request::<serde_json::Value>(
            Method::DELETE,
            &format!("branches/{}/", branch_id),
            None::<()>,
        ).await?;
        Ok(())
    }
}
