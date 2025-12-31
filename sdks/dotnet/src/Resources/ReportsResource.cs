using System.Collections.Generic;
using System.Threading.Tasks;

namespace Puxbay.SDK.Resources
{
    public class ReportsResource
    {
        private readonly PuxbayClient _client;
        public ReportsResource(PuxbayClient client) { _client = client; }

        public async Task<Dictionary<string, object>> FinancialSummaryAsync(string startDate, string endDate)
        {
            return await _client.GetAsync<Dictionary<string, object>>($"reports/financial-summary/?start_date={startDate}&end_date={endDate}");
        }

        public async Task<List<Dictionary<string, object>>> DailySalesAsync(string startDate, string endDate)
        {
            return await _client.GetAsync<List<Dictionary<string, object>>>($"reports/daily-sales/?start_date={startDate}&end_date={endDate}");
        }
        
        public async Task<List<Dictionary<string, object>>> TopProductsAsync(int limit = 10)
        {
             return await _client.GetAsync<List<Dictionary<string, object>>>($"reports/top-products/?limit={limit}");
        }
        
        public async Task<List<Dictionary<string, object>>> LowStockAsync()
        {
            return await _client.GetAsync<List<Dictionary<string, object>>>("reports/low-stock/");
        }
    }
}
