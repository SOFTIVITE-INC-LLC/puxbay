using System.Collections.Generic;
using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    public class GiftCardsResource
    {
        private readonly PuxbayClient _client;
        public GiftCardsResource(PuxbayClient client) { _client = client; }

        public async Task<PaginatedResponse<GiftCard>> ListAsync(int page = 1, string status = null)
        {
            string query = $"gift-cards/?page={page}";
            if (!string.IsNullOrEmpty(status)) query += $"&status={status}";
            return await _client.GetAsync<PaginatedResponse<GiftCard>>(query);
        }

        public async Task<GiftCard> GetAsync(string cardId)
        {
            return await _client.GetAsync<GiftCard>($"gift-cards/{cardId}/");
        }

        public async Task<GiftCard> CreateAsync(GiftCard card)
        {
            return await _client.PostAsync<GiftCard>("gift-cards/", card);
        }

        public async Task<GiftCard> RedeemAsync(string cardId, double amount)
        {
            return await _client.PostAsync<GiftCard>($"gift-cards/{cardId}/redeem/", new { amount });
        }
        
        public async Task<Dictionary<string, double>> CheckBalanceAsync(string code)
        {
            return await _client.GetAsync<Dictionary<string, double>>($"gift-cards/check-balance/?code={code}");
        }
    }
}
