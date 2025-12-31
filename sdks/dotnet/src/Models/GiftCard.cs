using System;
using Newtonsoft.Json;

namespace Puxbay.SDK.Models
{
    public class GiftCard
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("code")]
        public string Code { get; set; }

        [JsonProperty("balance")]
        public double Balance { get; set; }

        [JsonProperty("status")]
        public string Status { get; set; }

        [JsonProperty("expiry_date")]
        public DateTime? ExpiryDate { get; set; }
    }
}
