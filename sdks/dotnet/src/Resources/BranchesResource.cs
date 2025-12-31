using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    public class BranchesResource
    {
        private readonly PuxbayClient _client;
        public BranchesResource(PuxbayClient client) { _client = client; }

        public async Task<PaginatedResponse<Branch>> ListAsync(int page = 1)
        {
            return await _client.GetAsync<PaginatedResponse<Branch>>($"branches/?page={page}");
        }

        public async Task<Branch> GetAsync(string branchId)
        {
            return await _client.GetAsync<Branch>($"branches/{branchId}/");
        }

        public async Task<Branch> CreateAsync(Branch branch)
        {
            return await _client.PostAsync<Branch>("branches/", branch);
        }

        public async Task<Branch> UpdateAsync(string branchId, Branch branch)
        {
            return await _client.PatchAsync<Branch>($"branches/{branchId}/", branch);
        }

        public async Task DeleteAsync(string branchId)
        {
            await _client.DeleteAsync($"branches/{branchId}/");
        }
    }
}
