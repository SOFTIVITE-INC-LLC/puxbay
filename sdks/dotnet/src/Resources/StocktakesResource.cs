using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    public class StocktakesResource
    {
        private readonly PuxbayClient _client;
        public StocktakesResource(PuxbayClient client) { _client = client; }

        public async Task<PaginatedResponse<Stocktake>> ListAsync(int page = 1)
        {
            return await _client.GetAsync<PaginatedResponse<Stocktake>>($"stocktakes/?page={page}");
        }

        public async Task<Stocktake> GetAsync(string stocktakeId)
        {
            return await _client.GetAsync<Stocktake>($"stocktakes/{stocktakeId}/");
        }

        public async Task<Stocktake> CreateAsync(Stocktake stocktake)
        {
            return await _client.PostAsync<Stocktake>("stocktakes/", stocktake);
        }

        public async Task<Stocktake> CompleteAsync(string stocktakeId)
        {
            return await _client.PostAsync<Stocktake>($"stocktakes/{stocktakeId}/complete/", null);
        }
    }
}
