using System;
using Xunit;
using Puxbay.SDK;

namespace Puxbay.SDK.Tests
{
    public class PuxbayClientTests
    {
        [Fact]
        public void Initialization_ShouldThrow_WhenApiKeyIsInvalid()
        {
            var config = new PuxbayConfig { ApiKey = "invalid" };
            Assert.Throws<ArgumentException>(() => new PuxbayClient(config));
        }

        [Fact]
        public void Initialization_ShouldSucceed_WhenApiKeyIsValid()
        {
            var config = new PuxbayConfig { ApiKey = "pb_test" };
            using var client = new PuxbayClient(config);
            Assert.NotNull(client);
            Assert.NotNull(client.Products);
        }
    }
}
