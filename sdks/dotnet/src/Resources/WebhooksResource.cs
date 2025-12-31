using System.Collections.Generic;
using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    public class WebhooksResource
    {
        private readonly PuxbayClient _client;
        public WebhooksResource(PuxbayClient client) { _client = client; }

        public async Task<PaginatedResponse<Webhook>> ListAsync(int page = 1)
        {
            return await _client.GetAsync<PaginatedResponse<Webhook>>($"webhooks/?page={page}");
        }

        public async Task<Webhook> GetAsync(string webhookId)
        {
            return await _client.GetAsync<Webhook>($"webhooks/{webhookId}/");
        }

        public async Task<Webhook> CreateAsync(Webhook webhook)
        {
            return await _client.PostAsync<Webhook>("webhooks/", webhook);
        }

        public async Task<Webhook> UpdateAsync(string webhookId, Webhook webhook)
        {
            return await _client.PatchAsync<Webhook>($"webhooks/{webhookId}/", webhook);
        }

        public async Task DeleteAsync(string webhookId)
        {
            await _client.DeleteAsync($"webhooks/{webhookId}/");
        }
        
        public async Task<Dictionary<string, object>> ListEventsAsync(string webhookId, int page = 1)
        {
            return await _client.GetAsync<Dictionary<string, object>>($"webhook-logs/?webhook={webhookId}&page={page}");
        }
    }
}
