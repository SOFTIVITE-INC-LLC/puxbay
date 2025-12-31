use crate::models::{PaginatedResponse, Staff};
use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;

pub struct StaffResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> StaffResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn list(&self, page: i32, role: Option<&str>) -> Result<PaginatedResponse<Staff>, PuxbayError> {
        let mut query = format!("staff/?page={}", page);
        if let Some(r) = role {
            query.push_str(&format!("&role={}", r));
        }

        self.client.request(
            Method::GET,
            &query,
            None::<()>,
        ).await
    }

    pub async fn get(&self, staff_id: &str) -> Result<Staff, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("staff/{}/", staff_id),
            None::<()>,
        ).await
    }

    pub async fn create(&self, staff: &Staff) -> Result<Staff, PuxbayError> {
        self.client.request(
            Method::POST,
            "staff/",
            Some(staff),
        ).await
    }

    pub async fn update(&self, staff_id: &str, staff: &Staff) -> Result<Staff, PuxbayError> {
        self.client.request(
            Method::PATCH,
            &format!("staff/{}/", staff_id),
            Some(staff),
        ).await
    }

    pub async fn delete(&self, staff_id: &str) -> Result<(), PuxbayError> {
        self.client.request::<serde_json::Value>(
            Method::DELETE,
            &format!("staff/{}/", staff_id),
            None::<()>,
        ).await?;
        Ok(())
    }
}
