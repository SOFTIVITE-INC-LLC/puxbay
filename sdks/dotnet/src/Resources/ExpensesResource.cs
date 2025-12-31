using System.Collections.Generic;
using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    public class ExpensesResource
    {
        private readonly PuxbayClient _client;
        public ExpensesResource(PuxbayClient client) { _client = client; }

        public async Task<PaginatedResponse<Expense>> ListAsync(int page = 1, string category = null)
        {
            string query = $"expenses/?page={page}";
            if (!string.IsNullOrEmpty(category)) query += $"&category={category}";
            return await _client.GetAsync<PaginatedResponse<Expense>>(query);
        }

        public async Task<Expense> GetAsync(string expenseId)
        {
            return await _client.GetAsync<Expense>($"expenses/{expenseId}/");
        }

        public async Task<Expense> CreateAsync(Expense expense)
        {
            return await _client.PostAsync<Expense>("expenses/", expense);
        }

        public async Task<Expense> UpdateAsync(string expenseId, Expense expense)
        {
            return await _client.PatchAsync<Expense>($"expenses/{expenseId}/", expense);
        }

        public async Task DeleteAsync(string expenseId)
        {
            await _client.DeleteAsync($"expenses/{expenseId}/");
        }
        
        public async Task<List<string>> ListCategoriesAsync()
        {
            return await _client.GetAsync<List<string>>("expense-categories/");
        }
    }
}
