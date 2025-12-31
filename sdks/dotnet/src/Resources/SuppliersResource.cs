using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    public class SuppliersResource
    {
        private readonly PuxbayClient _client;
        public SuppliersResource(PuxbayClient client) { _client = client; }

        public async Task<PaginatedResponse<Supplier>> ListAsync(int page = 1, int pageSize = 20)
        {
            return await _client.GetAsync<PaginatedResponse<Supplier>>($"suppliers/?page={page}&page_size={pageSize}");
        }

        public async Task<Supplier> GetAsync(string supplierId)
        {
            return await _client.GetAsync<Supplier>($"suppliers/{supplierId}/");
        }

        public async Task<Supplier> CreateAsync(Supplier supplier)
        {
            return await _client.PostAsync<Supplier>("suppliers/", supplier);
        }

        public async Task<Supplier> UpdateAsync(string supplierId, Supplier supplier)
        {
            return await _client.PatchAsync<Supplier>($"suppliers/{supplierId}/", supplier);
        }

        public async Task DeleteAsync(string supplierId)
        {
            await _client.DeleteAsync($"suppliers/{supplierId}/");
        }
    }
}
