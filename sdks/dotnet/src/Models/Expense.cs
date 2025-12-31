using System;
using Newtonsoft.Json;

namespace Puxbay.SDK.Models
{
    public class Expense
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("category")]
        public string Category { get; set; }

        [JsonProperty("description")]
        public string Description { get; set; }

        [JsonProperty("amount")]
        public double Amount { get; set; }

        [JsonProperty("branch")]
        public string Branch { get; set; }

        [JsonProperty("receipt_url")]
        public string ReceiptUrl { get; set; }

        [JsonProperty("date")]
        public DateTime? Date { get; set; }
    }
}
