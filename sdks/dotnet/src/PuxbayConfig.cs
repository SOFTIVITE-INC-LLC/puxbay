using System;

namespace Puxbay.SDK
{
    /// <summary>
    /// Configuration for the Puxbay API client.
    /// </summary>
    public class PuxbayConfig
    {
        /// <summary>
        /// Gets or sets the API key (required, must start with 'pb_').
        /// </summary>
        public string ApiKey { get; set; }
        
        /// <summary>
        /// Gets or sets the base URL for the API.
        /// Default: https://api.puxbay.com/api/v1
        /// </summary>
        public string BaseUrl { get; set; } = "https://api.puxbay.com/api/v1";
        
        /// <summary>
        /// Gets or sets the request timeout.
        /// Default: 30 seconds
        /// </summary>
        public TimeSpan Timeout { get; set; } = TimeSpan.FromSeconds(30);
        
        /// <summary>
        /// Gets or sets the maximum number of retry attempts.
        /// Default: 3
        /// </summary>
        public int MaxRetries { get; set; } = 3;
        
        /// <summary>
        /// Gets or sets the maximum connections per server.
        /// Default: 10
        /// </summary>
        public int MaxConnectionsPerServer { get; set; } = 10;
    }
}
