using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace Puxbay.SDK.Models
{
    public class PurchaseOrder
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("po_number")]
        public string PoNumber { get; set; }

        [JsonProperty("supplier")]
        public string Supplier { get; set; }

        [JsonProperty("supplier_name")]
        public string SupplierName { get; set; }

        [JsonProperty("status")]
        public string Status { get; set; }

        [JsonProperty("total_amount")]
        public double TotalAmount { get; set; }

        [JsonProperty("expected_delivery_date")]
        public DateTime? ExpectedDeliveryDate { get; set; }

        // Keeping items as dynamic dictionary for simplicity in POCO if strict item type not defined
        [JsonProperty("items")]
        public List<Dictionary<string, object>> Items { get; set; }

        [JsonProperty("created_at")]
        public DateTime? CreatedAt { get; set; }

        [JsonProperty("updated_at")]
        public DateTime? UpdatedAt { get; set; }
    }
}
