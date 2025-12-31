use crate::models::{PaginatedResponse, Order};
use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;

pub struct OrdersResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> OrdersResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn list(&self, page: i32, page_size: i32) -> Result<PaginatedResponse<Order>, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("orders/?page={}&page_size={}", page, page_size),
            None::<()>,
        ).await
    }

    pub async fn get(&self, order_id: &str) -> Result<Order, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("orders/{}/", order_id),
            None::<()>,
        ).await
    }

    pub async fn create(&self, order: &Order) -> Result<Order, PuxbayError> {
        self.client.request(
            Method::POST,
            "orders/",
            Some(order),
        ).await
    }

    pub async fn cancel(&self, order_id: &str) -> Result<Order, PuxbayError> {
        self.client.request(
            Method::POST,
            &format!("orders/{}/cancel/", order_id),
            None::<()>,
        ).await
    }
}
