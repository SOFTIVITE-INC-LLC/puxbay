using System;
using Newtonsoft.Json;

namespace Puxbay.SDK.Models
{
    public class CashDrawerSession
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("branch")]
        public string Branch { get; set; }

        [JsonProperty("opened_by")]
        public string OpenedBy { get; set; }

        [JsonProperty("closed_by")]
        public string ClosedBy { get; set; }

        [JsonProperty("opening_cash")]
        public double OpeningCash { get; set; }

        [JsonProperty("closing_cash")]
        public double? ClosingCash { get; set; }

        [JsonProperty("actual_cash")]
        public double? ActualCash { get; set; }

        [JsonProperty("status")]
        public string Status { get; set; }

        [JsonProperty("opened_at")]
        public DateTime? OpenedAt { get; set; }

        [JsonProperty("closed_at")]
        public DateTime? ClosedAt { get; set; }
    }
}
