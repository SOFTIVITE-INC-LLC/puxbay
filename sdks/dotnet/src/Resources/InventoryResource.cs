using System.Collections.Generic;
using System.Threading.Tasks;

namespace Puxbay.SDK.Resources
{
    public class InventoryResource
    {
        private readonly PuxbayClient _client;
        public InventoryResource(PuxbayClient client) { _client = client; }

        public async Task<List<Dictionary<string, object>>> GetStockLevelsAsync(string branchId)
        {
            var response = await _client.GetAsync<Dictionary<string, List<Dictionary<string, object>>>>($"inventory/stock-levels/?branch={branchId}");
            return response["results"]; // Assuming standard DRF response wrapper for viewsets. Or custom
        }

        public async Task<Dictionary<string, object>> GetProductStockAsync(string productId, string branchId)
        {
            return await _client.GetAsync<Dictionary<string, object>>($"inventory/product-stock/?product={productId}&branch={branchId}");
        }
    }
}
