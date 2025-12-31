using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    public class ProductsResource
    {
        private readonly PuxbayClient _client;

        public ProductsResource(PuxbayClient client)
        {
            _client = client;
        }

        public async Task<PaginatedResponse<Product>> ListAsync(int page = 1, int pageSize = 20)
        {
            return await _client.GetAsync<PaginatedResponse<Product>>($"products/?page={page}&page_size={pageSize}");
        }

        public async Task<Product> GetAsync(string productId)
        {
            return await _client.GetAsync<Product>($"products/{productId}/");
        }

        public async Task<Product> CreateAsync(Product product)
        {
            return await _client.PostAsync<Product>("products/", product);
        }

        public async Task<Product> UpdateAsync(string productId, Product product)
        {
            return await _client.PatchAsync<Product>($"products/{productId}/", product);
        }

        public async Task DeleteAsync(string productId)
        {
            await _client.DeleteAsync($"products/{productId}/");
        }
    }
}
