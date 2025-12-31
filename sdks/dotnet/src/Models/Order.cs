using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace Puxbay.SDK.Models
{
    public class Order
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("order_number")]
        public string OrderNumber { get; set; }

        [JsonProperty("status")]
        public string Status { get; set; }

        [JsonProperty("subtotal")]
        public double Subtotal { get; set; }

        [JsonProperty("tax_amount")]
        public double TaxAmount { get; set; }

        [JsonProperty("total_amount")]
        public double TotalAmount { get; set; }

        [JsonProperty("amount_paid")]
        public double AmountPaid { get; set; }

        [JsonProperty("payment_method")]
        public string PaymentMethod { get; set; }

        [JsonProperty("ordering_type")]
        public string OrderingType { get; set; }

        [JsonProperty("offline_uuid")]
        public string OfflineUuid { get; set; }

        [JsonProperty("customer")]
        public string Customer { get; set; }

        [JsonProperty("customer_name")]
        public string CustomerName { get; set; }

        [JsonProperty("cashier")]
        public string Cashier { get; set; }

        [JsonProperty("cashier_name")]
        public string CashierName { get; set; }

        [JsonProperty("branch")]
        public string Branch { get; set; }

        [JsonProperty("branch_name")]
        public string BranchName { get; set; }

        [JsonProperty("items")]
        public List<OrderItem> Items { get; set; }

        [JsonProperty("created_at")]
        public DateTime? CreatedAt { get; set; }

        [JsonProperty("updated_at")]
        public DateTime? UpdatedAt { get; set; }
    }
}
