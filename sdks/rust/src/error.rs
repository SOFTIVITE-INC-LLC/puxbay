use thiserror::Error;
use serde::Deserialize;

/// Puxbay error types
#[derive(Error, Debug)]
pub enum PuxbayError {
    #[error("Invalid API key format. Must start with 'pb_'")]
    InvalidApiKey,
    
    #[error("Authentication error: {0}")]
    AuthenticationError(String),
    
    #[error("Rate limit error: {0}")]
    RateLimitError(String),
    
    #[error("Validation error: {0}")]
    ValidationError(String),
    
    #[error("Not found error: {0}")]
    NotFoundError(String),
    
    #[error("Server error: {0}")]
    ServerError(String),
    
    #[error("API error: {0} (status: {1})")]
    ApiError(String, u16),
    
    #[error("Request error: {0}")]
    RequestError(#[from] reqwest::Error),
    
    #[error("Unknown error")]
    UnknownError,
}

#[derive(Deserialize)]
pub(crate) struct ErrorResponse {
    pub detail: Option<String>,
    pub message: Option<String>,
}
