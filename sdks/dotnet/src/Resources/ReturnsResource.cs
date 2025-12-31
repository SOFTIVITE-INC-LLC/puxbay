using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    public class ReturnsResource
    {
        private readonly PuxbayClient _client;
        public ReturnsResource(PuxbayClient client) { _client = client; }

        public async Task<PaginatedResponse<ReturnRequest>> ListAsync(int page = 1)
        {
            return await _client.GetAsync<PaginatedResponse<ReturnRequest>>($"returns/?page={page}");
        }

        public async Task<ReturnRequest> GetAsync(string returnId)
        {
            return await _client.GetAsync<ReturnRequest>($"returns/{returnId}/");
        }

        public async Task<ReturnRequest> CreateAsync(ReturnRequest returnReq)
        {
            return await _client.PostAsync<ReturnRequest>("returns/", returnReq);
        }

        public async Task<ReturnRequest> ApproveAsync(string returnId)
        {
            return await _client.PostAsync<ReturnRequest>($"returns/{returnId}/approve/", null);
        }
    }
}
