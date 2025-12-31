use puxbay_sdk::{Puxbay, PuxbayConfig};
use std::error::Error;
use std::env;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let api_key = env::var("PUXBAY_API_KEY").expect("PUXBAY_API_KEY must be set");
    
    let config = PuxbayConfig::builder()
        .api_key(&api_key)
        .build();

    let client = Puxbay::new(config);

    println!("Fetching products...");
    let products = client.products().list(1).await?;

    for product in products.results {
        println!("- {} (${})", product.name, product.price);
    }
    
    Ok(())
}
