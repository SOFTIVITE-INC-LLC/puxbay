using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    public class OrdersResource
    {
        private readonly PuxbayClient _client;

        public OrdersResource(PuxbayClient client)
        {
            _client = client;
        }

        public async Task<PaginatedResponse<Order>> ListAsync(int page = 1, int pageSize = 20)
        {
            return await _client.GetAsync<PaginatedResponse<Order>>($"orders/?page={page}&page_size={pageSize}");
        }

        public async Task<Order> GetAsync(string orderId)
        {
            return await _client.GetAsync<Order>($"orders/{orderId}/");
        }

        public async Task<Order> CreateAsync(Order order)
        {
            return await _client.PostAsync<Order>("orders/", order);
        }

        public async Task<Order> CancelAsync(string orderId)
        {
            await _client.PostAsync<object>($"orders/{orderId}/cancel/", null);
            return await GetAsync(orderId);
        }
    }
}
