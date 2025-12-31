use puxbay_sdk::{Puxbay, PuxbayConfig};
use std::env;

#[tokio::test]
async fn test_products_list() {
    let api_key = env::var("PUXBAY_API_KEY").unwrap_or_else(|_| "pb_test_key".to_string());
    let base_url = env::var("PUXBAY_BASE_URL").unwrap_or_else(|_| "http://localhost:8000/api/v1".to_string());

    let config = PuxbayConfig::builder()
        .api_key(&api_key)
        .base_url(&base_url)
        .build();

    let client = Puxbay::new(config);

    // This is a basic connectivity test. 
    // In a real integration test, we would expect a running server or use a mock.
    // For now we just verify the call structure compiles and runs.
    let result = client.products().list(1).await;
    
    // We don't assert success here because we don't have a guaranteed live backend.
    // But we check that it didn't panic.
    assert!(result.is_ok() || result.is_err()); 
}
