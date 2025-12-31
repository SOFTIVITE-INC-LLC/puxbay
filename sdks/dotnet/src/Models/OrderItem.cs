using Newtonsoft.Json;

namespace Puxbay.SDK.Models
{
    public class OrderItem
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("product")]
        public string Product { get; set; }

        [JsonProperty("product_name")]
        public string ProductName { get; set; }

        [JsonProperty("sku")]
        public string Sku { get; set; }

        [JsonProperty("item_number")]
        public string ItemNumber { get; set; }

        [JsonProperty("quantity")]
        public int Quantity { get; set; }

        [JsonProperty("price")]
        public double Price { get; set; }

        [JsonProperty("cost_price")]
        public double? CostPrice { get; set; }

        [JsonProperty("total_price")]
        public double TotalPrice { get; set; }
    }
}
