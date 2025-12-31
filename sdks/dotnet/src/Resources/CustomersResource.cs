using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    public class CustomersResource
    {
        private readonly PuxbayClient _client;

        public CustomersResource(PuxbayClient client)
        {
            _client = client;
        }

        public async Task<PaginatedResponse<Customer>> ListAsync(int page = 1, int pageSize = 20)
        {
            return await _client.GetAsync<PaginatedResponse<Customer>>($"customers/?page={page}&page_size={pageSize}");
        }

        public async Task<Customer> GetAsync(string customerId)
        {
            return await _client.GetAsync<Customer>($"customers/{customerId}/");
        }

        public async Task<Customer> CreateAsync(Customer customer)
        {
            return await _client.PostAsync<Customer>("customers/", customer);
        }

        public async Task<Customer> UpdateAsync(string customerId, Customer customer)
        {
            return await _client.PatchAsync<Customer>($"customers/{customerId}/", customer);
        }

        public async Task DeleteAsync(string customerId)
        {
            await _client.DeleteAsync($"customers/{customerId}/");
        }
    }
}
