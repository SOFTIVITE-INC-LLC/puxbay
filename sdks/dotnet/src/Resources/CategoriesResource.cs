using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    public class CategoriesResource
    {
        private readonly PuxbayClient _client;
        public CategoriesResource(PuxbayClient client) { _client = client; }

        public async Task<PaginatedResponse<Category>> ListAsync(int page = 1)
        {
            return await _client.GetAsync<PaginatedResponse<Category>>($"categories/?page={page}");
        }

        public async Task<Category> GetAsync(string categoryId)
        {
            return await _client.GetAsync<Category>($"categories/{categoryId}/");
        }

        public async Task<Category> CreateAsync(Category category)
        {
            return await _client.PostAsync<Category>("categories/", category);
        }

        public async Task<Category> UpdateAsync(string categoryId, Category category)
        {
            return await _client.PatchAsync<Category>($"categories/{categoryId}/", category);
        }

        public async Task DeleteAsync(string categoryId)
        {
            await _client.DeleteAsync($"categories/{categoryId}/");
        }
    }
}
