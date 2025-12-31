using System.Collections.Generic;
using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    public class PurchaseOrdersResource
    {
        private readonly PuxbayClient _client;
        public PurchaseOrdersResource(PuxbayClient client) { _client = client; }

        public async Task<PaginatedResponse<PurchaseOrder>> ListAsync(int page = 1, string status = null)
        {
            string query = $"purchase-orders/?page={page}";
            if (!string.IsNullOrEmpty(status)) query += $"&status={status}";
            return await _client.GetAsync<PaginatedResponse<PurchaseOrder>>(query);
        }

        public async Task<PurchaseOrder> GetAsync(string poId)
        {
            return await _client.GetAsync<PurchaseOrder>($"purchase-orders/{poId}/");
        }

        public async Task<PurchaseOrder> CreateAsync(PurchaseOrder po)
        {
            return await _client.PostAsync<PurchaseOrder>("purchase-orders/", po);
        }

        public async Task<PurchaseOrder> UpdateAsync(string poId, PurchaseOrder po)
        {
            return await _client.PatchAsync<PurchaseOrder>($"purchase-orders/{poId}/", po);
        }

        public async Task<PurchaseOrder> ReceiveAsync(string poId, List<Dictionary<string, object>> items)
        {
            return await _client.PostAsync<PurchaseOrder>($"purchase-orders/{poId}/receive/", new { items });
        }
    }
}
