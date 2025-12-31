using System.Collections.Generic;
using Newtonsoft.Json;

namespace Puxbay.SDK.Models
{
    public class PaginatedResponse<T>
    {
        [JsonProperty("count")]
        public int Count { get; set; }

        [JsonProperty("next")]
        public string Next { get; set; }

        [JsonProperty("previous")]
        public string Previous { get; set; }

        [JsonProperty("results")]
        public List<T> Results { get; set; }
    }
}
