using System;
using System.Threading.Tasks;
using Puxbay.SDK;

namespace ListProducts
{
    class Program
    {
        static async Task Main(string[] args)
        {
            var apiKey = Environment.GetEnvironmentVariable("PUXBAY_API_KEY");
            if (string.IsNullOrEmpty(apiKey))
            {
                Console.WriteLine("PUXBAY_API_KEY must be set");
                return;
            }

            var config = new PuxbayConfig { ApiKey = apiKey };
            using var client = new PuxbayClient(config);

            try
            {
                Console.WriteLine("Fetching products...");
                var response = await client.Products.ListAsync(1, 20);

                foreach (var product in response.Results)
                {
                    Console.WriteLine($"- {product.Name} (${product.Price})");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
        }
    }
}
