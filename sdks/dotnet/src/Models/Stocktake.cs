using System;
using Newtonsoft.Json;

namespace Puxbay.SDK.Models
{
    public class Stocktake
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("branch")]
        public string Branch { get; set; }

        [JsonProperty("status")]
        public string Status { get; set; }

        [JsonProperty("notes")]
        public string Notes { get; set; }

        [JsonProperty("created_at")]
        public DateTime? CreatedAt { get; set; }

        [JsonProperty("updated_at")]
        public DateTime? UpdatedAt { get; set; }
    }
}
