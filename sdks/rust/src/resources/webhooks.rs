use crate::models::{PaginatedResponse, Webhook};
use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;
use std::collections::HashMap;

pub struct WebhooksResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> WebhooksResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn list(&self, page: i32) -> Result<PaginatedResponse<Webhook>, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("webhooks/?page={}", page),
            None::<()>,
        ).await
    }

    pub async fn get(&self, webhook_id: &str) -> Result<Webhook, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("webhooks/{}/", webhook_id),
            None::<()>,
        ).await
    }

    pub async fn create(&self, webhook: &Webhook) -> Result<Webhook, PuxbayError> {
        self.client.request(
            Method::POST,
            "webhooks/",
            Some(webhook),
        ).await
    }

    pub async fn update(&self, webhook_id: &str, webhook: &Webhook) -> Result<Webhook, PuxbayError> {
        self.client.request(
            Method::PATCH,
            &format!("webhooks/{}/", webhook_id),
            Some(webhook),
        ).await
    }

    pub async fn delete(&self, webhook_id: &str) -> Result<(), PuxbayError> {
        self.client.request::<serde_json::Value>(
            Method::DELETE,
            &format!("webhooks/{}/", webhook_id),
            None::<()>,
        ).await?;
        Ok(())
    }

    pub async fn list_events(&self, webhook_id: &str, page: i32) -> Result<HashMap<String, serde_json::Value>, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("webhook-logs/?webhook={}&page={}", webhook_id, page),
            None::<()>,
        ).await
    }
}
