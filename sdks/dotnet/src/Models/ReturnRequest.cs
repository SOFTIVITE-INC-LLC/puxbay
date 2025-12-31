using System;
using Newtonsoft.Json;

namespace Puxbay.SDK.Models
{
    public class ReturnRequest
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("order")]
        public string Order { get; set; }

        [JsonProperty("status")]
        public string Status { get; set; }

        [JsonProperty("reason")]
        public string Reason { get; set; }

        [JsonProperty("refund_amount")]
        public double RefundAmount { get; set; }

        [JsonProperty("created_at")]
        public DateTime? CreatedAt { get; set; }

        [JsonProperty("updated_at")]
        public DateTime? UpdatedAt { get; set; }
    }
}
