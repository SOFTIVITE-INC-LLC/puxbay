using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace Puxbay.SDK.Models
{
    public class Webhook
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("url")]
        public string Url { get; set; }

        [JsonProperty("events")]
        public List<string> Events { get; set; }

        [JsonProperty("is_active")]
        public bool IsActive { get; set; }

        [JsonProperty("secret")]
        public string Secret { get; set; }

        [JsonProperty("created_at")]
        public DateTime? CreatedAt { get; set; }
    }
}
