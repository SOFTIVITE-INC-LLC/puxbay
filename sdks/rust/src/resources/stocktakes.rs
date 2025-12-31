use crate::models::{PaginatedResponse, Stocktake};
use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;

pub struct StocktakesResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> StocktakesResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn list(&self, page: i32) -> Result<PaginatedResponse<Stocktake>, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("stocktakes/?page={}", page),
            None::<()>,
        ).await
    }

    pub async fn get(&self, stocktake_id: &str) -> Result<Stocktake, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("stocktakes/{}/", stocktake_id),
            None::<()>,
        ).await
    }

    pub async fn create(&self, stocktake: &Stocktake) -> Result<Stocktake, PuxbayError> {
        self.client.request(
            Method::POST,
            "stocktakes/",
            Some(stocktake),
        ).await
    }

    pub async fn complete(&self, stocktake_id: &str) -> Result<Stocktake, PuxbayError> {
        self.client.request(
            Method::POST,
            &format!("stocktakes/{}/complete/", stocktake_id),
            None::<()>,
        ).await
    }
}
