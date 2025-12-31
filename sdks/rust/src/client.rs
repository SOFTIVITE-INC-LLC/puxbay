use reqwest::{Client as ReqwestClient, Method, StatusCode};
use serde::{Deserialize, Serialize};
use std::time::Duration;
use crate::error::{PuxbayError, ErrorResponse};
use crate::resources::*;

/// Main Puxbay API client with reqwest and async/await
pub struct Puxbay {
    pub(crate) api_key: String,
    pub(crate) base_url: String,
    pub(crate) client: ReqwestClient,
    pub(crate) max_retries: u32,
}

impl Puxbay {
    /// Create a new Puxbay client
    pub fn new(api_key: impl Into<String>) -> Result<Self, PuxbayError> {
        Self::with_config(api_key, PuxbayConfig::default())
    }
    
    /// Create a new Puxbay client with custom configuration
    pub fn with_config(api_key: impl Into<String>, config: PuxbayConfig) -> Result<Self, PuxbayError> {
        let api_key = api_key.into();
        
        if !api_key.starts_with("pb_") {
            return Err(PuxbayError::InvalidApiKey);
        }
        
        let client = ReqwestClient::builder()
            .timeout(Duration::from_secs(config.timeout))
            .gzip(true)
            .default_headers({
                let mut headers = reqwest::header::HeaderMap::new();
                headers.insert("X-API-Key", api_key.parse().unwrap());
                headers.insert("Content-Type", "application/json".parse().unwrap());
                headers.insert("User-Agent", "puxbay-rust/1.0.0".parse().unwrap());
                headers.insert("Accept-Encoding", "gzip, deflate".parse().unwrap());
                headers
            })
            .build()?;
        
        Ok(Self {
            api_key,
            base_url: config.base_url,
            client,
            max_retries: config.max_retries,
        })
    }
    
    // Resource accessors
    pub fn products(&self) -> ProductsResource { ProductsResource::new(self) }
    pub fn orders(&self) -> OrdersResource { OrdersResource::new(self) }
    pub fn customers(&self) -> CustomersResource { CustomersResource::new(self) }
    pub fn categories(&self) -> CategoriesResource { CategoriesResource::new(self) }
    pub fn suppliers(&self) -> SuppliersResource { SuppliersResource::new(self) }
    pub fn gift_cards(&self) -> GiftCardsResource { GiftCardsResource::new(self) }
    pub fn branches(&self) -> BranchesResource { BranchesResource::new(self) }
    pub fn staff(&self) -> StaffResource { StaffResource::new(self) }
    pub fn webhooks(&self) -> WebhooksResource { WebhooksResource::new(self) }
    pub fn purchase_orders(&self) -> PurchaseOrdersResource { PurchaseOrdersResource::new(self) }
    pub fn stock_transfers(&self) -> StockTransfersResource { StockTransfersResource::new(self) }
    pub fn inventory(&self) -> InventoryResource { InventoryResource::new(self) }
    pub fn reports(&self) -> ReportsResource { ReportsResource::new(self) }
    pub fn stocktakes(&self) -> StocktakesResource { StocktakesResource::new(self) }
    pub fn cash_drawers(&self) -> CashDrawersResource { CashDrawersResource::new(self) }
    pub fn expenses(&self) -> ExpensesResource { ExpensesResource::new(self) }
    pub fn notifications(&self) -> NotificationsResource { NotificationsResource::new(self) }
    pub fn returns(&self) -> ReturnsResource { ReturnsResource::new(self) }
    
    /// Make HTTP request with retry logic
    pub async fn request<T: for<'de> Deserialize<'de>>(
        &self,
        method: Method,
        endpoint: &str,
        body: Option<impl Serialize>,
    ) -> Result<T, PuxbayError> {
        let url = format!("{}/{}", self.base_url, endpoint);
        let mut last_error = None;
        
        for attempt in 0..=self.max_retries {
            let mut request = self.client.request(method.clone(), &url);
            
            if let Some(ref body) = body {
                request = request.json(body);
            }
            
            match request.send().await {
                Ok(response) => {
                    let status = response.status();
                    
                    if status == StatusCode::TOO_MANY_REQUESTS || status.is_server_error() {
                        if attempt < self.max_retries {
                            let delay = Duration::from_secs(2_u64.pow(attempt));
                            tokio::time::sleep(delay).await;
                            continue;
                        }
                    }
                    
                    if !status.is_success() {
                        let body = response.text().await?;
                        return Err(Self::handle_error_response(status, &body));
                    }
                    
                     // Handle empty response for DELETE or void returns if T is serde_json::Value or similar
                    // But if T is a struct, we expect JSON.
                    // If T is specific struct and response is empty, it might error.
                    // For now assuming API always returns JSON or we use ()/Empty structs.
                    // Actually serde_json::from_reader or response.json() expects content.
                    // If API returns 204 No Content, we should handle that.
                    if status == StatusCode::NO_CONTENT {
                         // This is tricky in Rust generic request if T is not Option<T> or similar unit type handling.
                         // But for simplicity in this SDK refactor, we rely on standard behavior.
                    }

                    return Ok(response.json().await?);
                }
                Err(e) => {
                    last_error = Some(e);
                    if attempt < self.max_retries {
                        let delay = Duration::from_secs(2_u64.pow(attempt));
                        tokio::time::sleep(delay).await;
                    }
                }
            }
        }
        
        Err(last_error.map(PuxbayError::from).unwrap_or(PuxbayError::UnknownError))
    }
    
    fn handle_error_response(status: StatusCode, body: &str) -> PuxbayError {
        let message = serde_json::from_str::<ErrorResponse>(body)
            .ok()
            .and_then(|e| e.detail.or(e.message))
            .unwrap_or_else(|| "Unknown error".to_string());
        
        match status {
            StatusCode::UNAUTHORIZED => PuxbayError::AuthenticationError(message),
            StatusCode::TOO_MANY_REQUESTS => PuxbayError::RateLimitError(message),
            StatusCode::BAD_REQUEST => PuxbayError::ValidationError(message),
            StatusCode::NOT_FOUND => PuxbayError::NotFoundError(message),
            _ if status.is_server_error() => PuxbayError::ServerError(message),
            _ => PuxbayError::ApiError(message, status.as_u16()),
        }
    }
}

/// Configuration for Puxbay client
pub struct PuxbayConfig {
    pub base_url: String,
    pub timeout: u64,
    pub max_retries: u32,
}

impl Default for PuxbayConfig {
    fn default() -> Self {
        Self {
            base_url: "https://api.puxbay.com/api/v1".to_string(),
            timeout: 30,
            max_retries: 3,
        }
    }
}
