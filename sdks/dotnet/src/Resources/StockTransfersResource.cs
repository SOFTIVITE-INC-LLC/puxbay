using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    public class StockTransfersResource
    {
        private readonly PuxbayClient _client;
        public StockTransfersResource(PuxbayClient client) { _client = client; }

        public async Task<PaginatedResponse<StockTransfer>> ListAsync(int page = 1, string status = null)
        {
            string query = $"stock-transfers/?page={page}";
            if (!string.IsNullOrEmpty(status)) query += $"&status={status}";
            return await _client.GetAsync<PaginatedResponse<StockTransfer>>(query);
        }

        public async Task<StockTransfer> GetAsync(string transferId)
        {
            return await _client.GetAsync<StockTransfer>($"stock-transfers/{transferId}/");
        }

        public async Task<StockTransfer> CreateAsync(StockTransfer transfer)
        {
            return await _client.PostAsync<StockTransfer>("stock-transfers/", transfer);
        }

        public async Task<StockTransfer> CompleteAsync(string transferId)
        {
            return await _client.PostAsync<StockTransfer>($"stock-transfers/{transferId}/complete/", null);
        }
    }
}
