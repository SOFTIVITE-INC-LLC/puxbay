using System.Collections.Generic;
using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    public class CashDrawersResource
    {
        private readonly PuxbayClient _client;
        public CashDrawersResource(PuxbayClient client) { _client = client; }

        public async Task<PaginatedResponse<CashDrawerSession>> ListAsync(int page = 1)
        {
            return await _client.GetAsync<PaginatedResponse<CashDrawerSession>>($"cash-drawers/?page={page}");
        }

        public async Task<CashDrawerSession> GetAsync(string drawerId)
        {
            return await _client.GetAsync<CashDrawerSession>($"cash-drawers/{drawerId}/");
        }

        public async Task<CashDrawerSession> OpenAsync(Dictionary<string, object> drawerData)
        {
            return await _client.PostAsync<CashDrawerSession>("cash-drawers/", drawerData);
        }

        public async Task<CashDrawerSession> CloseAsync(string drawerId, double actualCash)
        {
            return await _client.PostAsync<CashDrawerSession>($"cash-drawers/{drawerId}/close/", new { actual_cash = actualCash });
        }
    }
}
