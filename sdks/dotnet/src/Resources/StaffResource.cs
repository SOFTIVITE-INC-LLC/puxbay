using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    public class StaffResource
    {
        private readonly PuxbayClient _client;
        public StaffResource(PuxbayClient client) { _client = client; }

        public async Task<PaginatedResponse<Staff>> ListAsync(int page = 1, string role = null)
        {
            string query = $"staff/?page={page}";
            if (!string.IsNullOrEmpty(role)) query += $"&role={role}";
            return await _client.GetAsync<PaginatedResponse<Staff>>(query);
        }

        public async Task<Staff> GetAsync(string staffId)
        {
            return await _client.GetAsync<Staff>($"staff/{staffId}/");
        }

        public async Task<Staff> CreateAsync(Staff staff)
        {
            return await _client.PostAsync<Staff>("staff/", staff);
        }

        public async Task<Staff> UpdateAsync(string staffId, Staff staff)
        {
            return await _client.PatchAsync<Staff>($"staff/{staffId}/", staff);
        }

        public async Task DeleteAsync(string staffId)
        {
            await _client.DeleteAsync($"staff/{staffId}/");
        }
    }
}
