using System.Threading.Tasks;
using Puxbay.SDK.Models;

namespace Puxbay.SDK.Resources
{
    public class NotificationsResource
    {
        private readonly PuxbayClient _client;
        public NotificationsResource(PuxbayClient client) { _client = client; }

        public async Task<PaginatedResponse<Notification>> ListAsync(int page = 1)
        {
            return await _client.GetAsync<PaginatedResponse<Notification>>($"notifications/?page={page}");
        }

        public async Task<Notification> GetAsync(string notificationId)
        {
            return await _client.GetAsync<Notification>($"notifications/{notificationId}/");
        }

        public async Task<Notification> MarkAsReadAsync(string notificationId)
        {
            return await _client.PostAsync<Notification>($"notifications/{notificationId}/mark-read/", null);
        }
    }
}
