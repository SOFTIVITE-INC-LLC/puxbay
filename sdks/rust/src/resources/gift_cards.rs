use crate::models::{PaginatedResponse, GiftCard};
use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;
use serde::Serialize;
use std::collections::HashMap;

pub struct GiftCardsResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> GiftCardsResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn list(&self, page: i32, status: Option<&str>) -> Result<PaginatedResponse<GiftCard>, PuxbayError> {
        let mut query = format!("gift-cards/?page={}", page);
        if let Some(s) = status {
            query.push_str(&format!("&status={}", s));
        }
        
        self.client.request(
            Method::GET,
            &query,
            None::<()>,
        ).await
    }

    pub async fn get(&self, card_id: &str) -> Result<GiftCard, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("gift-cards/{}/", card_id),
            None::<()>,
        ).await
    }

    pub async fn create(&self, card: &GiftCard) -> Result<GiftCard, PuxbayError> {
        self.client.request(
            Method::POST,
            "gift-cards/",
            Some(card),
        ).await
    }

    pub async fn redeem(&self, card_id: &str, amount: f64) -> Result<GiftCard, PuxbayError> {
        #[derive(Serialize)]
        struct RedeemRequest {
            amount: f64,
        }

        self.client.request(
            Method::POST,
            &format!("gift-cards/{}/redeem/", card_id),
            Some(&RedeemRequest { amount }),
        ).await
    }

    pub async fn check_balance(&self, code: &str) -> Result<HashMap<String, f64>, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("gift-cards/check-balance/?code={}", code),
            None::<()>,
        ).await
    }
}
