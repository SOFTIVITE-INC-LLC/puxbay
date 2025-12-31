use crate::models::{PaginatedResponse, Notification};
use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;

pub struct NotificationsResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> NotificationsResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn list(&self, page: i32) -> Result<PaginatedResponse<Notification>, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("notifications/?page={}", page),
            None::<()>,
        ).await
    }

    pub async fn get(&self, notification_id: &str) -> Result<Notification, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("notifications/{}/", notification_id),
            None::<()>,
        ).await
    }

    pub async fn mark_as_read(&self, notification_id: &str) -> Result<Notification, PuxbayError> {
        self.client.request(
            Method::POST,
            &format!("notifications/{}/mark-read/", notification_id),
            None::<()>,
        ).await
    }
}
