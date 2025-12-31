using System;
using Newtonsoft.Json;

namespace Puxbay.SDK.Models
{
    public class Customer
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("name")]
        public string Name { get; set; }

        [JsonProperty("email")]
        public string Email { get; set; }

        [JsonProperty("phone")]
        public string Phone { get; set; }

        [JsonProperty("address")]
        public string Address { get; set; }

        [JsonProperty("customer_type")]
        public string CustomerType { get; set; }

        [JsonProperty("loyalty_points")]
        public int LoyaltyPoints { get; set; }

        [JsonProperty("store_credit_balance")]
        public double StoreCreditBalance { get; set; }

        [JsonProperty("total_spend")]
        public double TotalSpend { get; set; }

        [JsonProperty("tier")]
        public string Tier { get; set; }

        [JsonProperty("tier_name")]
        public string TierName { get; set; }

        [JsonProperty("marketing_opt_in")]
        public bool MarketingOptIn { get; set; }

        [JsonProperty("created_at")]
        public DateTime? CreatedAt { get; set; }
    }
}
