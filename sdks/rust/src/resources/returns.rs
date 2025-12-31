use crate::models::{PaginatedResponse, ReturnRequest};
use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;

pub struct ReturnsResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> ReturnsResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn list(&self, page: i32) -> Result<PaginatedResponse<ReturnRequest>, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("returns/?page={}", page),
            None::<()>,
        ).await
    }

    pub async fn get(&self, return_id: &str) -> Result<ReturnRequest, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("returns/{}/", return_id),
            None::<()>,
        ).await
    }

    pub async fn create(&self, return_req: &ReturnRequest) -> Result<ReturnRequest, PuxbayError> {
        self.client.request(
            Method::POST,
            "returns/",
            Some(return_req),
        ).await
    }

    pub async fn approve(&self, return_id: &str) -> Result<ReturnRequest, PuxbayError> {
        self.client.request(
            Method::POST,
            &format!("returns/{}/approve/", return_id),
            None::<()>,
        ).await
    }
}
