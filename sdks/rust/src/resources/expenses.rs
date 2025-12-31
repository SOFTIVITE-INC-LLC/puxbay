use crate::models::{PaginatedResponse, Expense};
use crate::Puxbay;
use crate::PuxbayError;
use reqwest::Method;

pub struct ExpensesResource<'a> {
    pub(crate) client: &'a Puxbay,
}

impl<'a> ExpensesResource<'a> {
    pub fn new(client: &'a Puxbay) -> Self {
        Self { client }
    }

    pub async fn list(&self, page: i32, category: Option<&str>) -> Result<PaginatedResponse<Expense>, PuxbayError> {
         let mut query = format!("expenses/?page={}", page);
        if let Some(c) = category {
            query.push_str(&format!("&category={}", c));
        }

        self.client.request(
            Method::GET,
            &query,
            None::<()>,
        ).await
    }

    pub async fn get(&self, expense_id: &str) -> Result<Expense, PuxbayError> {
        self.client.request(
            Method::GET,
            &format!("expenses/{}/", expense_id),
            None::<()>,
        ).await
    }

    pub async fn create(&self, expense: &Expense) -> Result<Expense, PuxbayError> {
        self.client.request(
            Method::POST,
            "expenses/",
            Some(expense),
        ).await
    }

    pub async fn update(&self, expense_id: &str, expense: &Expense) -> Result<Expense, PuxbayError> {
        self.client.request(
            Method::PATCH,
            &format!("expenses/{}/", expense_id),
            Some(expense),
        ).await
    }

    pub async fn delete(&self, expense_id: &str) -> Result<(), PuxbayError> {
        self.client.request::<serde_json::Value>(
            Method::DELETE,
            &format!("expenses/{}/", expense_id),
            None::<()>,
        ).await?;
        Ok(())
    }

    pub async fn list_categories(&self) -> Result<Vec<String>, PuxbayError> {
        self.client.request(
            Method::GET,
            "expense-categories/",
            None::<()>,
        ).await
    }
}
