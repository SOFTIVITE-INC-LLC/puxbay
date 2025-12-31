use crate::models::{PaginatedResponse, Customer};
use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;
use serde::Serialize;

pub struct CustomersResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> CustomersResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn list(&self, page: i32, page_size: i32) -> Result<PaginatedResponse<Customer>, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("customers/?page={}&page_size={}", page, page_size),
            None::<()>,
        ).await
    }

    pub async fn get(&self, customer_id: &str) -> Result<Customer, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("customers/{}/", customer_id),
            None::<()>,
        ).await
    }

    pub async fn create(&self, customer: &Customer) -> Result<Customer, PuxbayError> {
        self.client.request(
            Method::POST,
            "customers/",
            Some(customer),
        ).await
    }

    pub async fn update(&self, customer_id: &str, customer: &Customer) -> Result<Customer, PuxbayError> {
        self.client.request(
            Method::PATCH,
            &format!("customers/{}/", customer_id),
            Some(customer),
        ).await
    }

    pub async fn delete(&self, customer_id: &str) -> Result<(), PuxbayError> {
        self.client.request::<serde_json::Value>(
            Method::DELETE,
            &format!("customers/{}/", customer_id),
            None::<()>,
        ).await?;
        Ok(())
    }

    pub async fn adjust_loyalty_points(&self, customer_id: &str, points: i32, description: &str) -> Result<Customer, PuxbayError> {
         #[derive(Serialize)]
        struct AdjustPointsRequest<'a> {
            points: i32,
            description: &'a str,
        }

        self.client.request(
            Method::POST,
            &format!("customers/{}/adjust-loyalty-points/", customer_id),
            Some(&AdjustPointsRequest { points, description }),
        ).await
    }
}
