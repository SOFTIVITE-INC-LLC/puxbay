using Newtonsoft.Json;

namespace Puxbay.SDK.Models
{
    public class Staff
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("username")]
        public string Username { get; set; }

        [JsonProperty("full_name")]
        public string FullName { get; set; }

        [JsonProperty("email")]
        public string Email { get; set; }

        [JsonProperty("role")]
        public string Role { get; set; }

        [JsonProperty("branch")]
        public string Branch { get; set; }

        [JsonProperty("branch_name")]
        public string BranchName { get; set; }
    }
}
