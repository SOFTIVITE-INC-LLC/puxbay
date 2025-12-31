using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace Puxbay.SDK.Models
{
    public class StockTransfer
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("source_branch")]
        public string SourceBranch { get; set; }

        [JsonProperty("source_branch_name")]
        public string SourceBranchName { get; set; }

        [JsonProperty("destination_branch")]
        public string DestinationBranch { get; set; }

        [JsonProperty("destination_branch_name")]
        public string DestinationBranchName { get; set; }

        [JsonProperty("status")]
        public string Status { get; set; }

        [JsonProperty("items")]
        public List<Dictionary<string, object>> Items { get; set; }

        [JsonProperty("notes")]
        public string Notes { get; set; }

        [JsonProperty("created_at")]
        public DateTime? CreatedAt { get; set; }

        [JsonProperty("updated_at")]
        public DateTime? UpdatedAt { get; set; }
    }
}
