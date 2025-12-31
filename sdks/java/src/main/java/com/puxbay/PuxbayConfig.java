package com.puxbay;

/**
 * Configuration for the Puxbay API client.
 */
public class PuxbayConfig {
    private final String apiKey;
    private final String baseUrl;
    private final int timeout;
    private final int maxRetries;
    private final int maxIdleConnections;
    private final long keepAliveDuration;
    
    private PuxbayConfig(Builder builder) {
        this.apiKey = builder.apiKey;
        this.baseUrl = builder.baseUrl;
        this.timeout = builder.timeout;
        this.maxRetries = builder.maxRetries;
        this.maxIdleConnections = builder.maxIdleConnections;
        this.keepAliveDuration = builder.keepAliveDuration;
    }
    
    public String getApiKey() { return apiKey; }
    public String getBaseUrl() { return baseUrl; }
    public int getTimeout() { return timeout; }
    public int getMaxRetries() { return maxRetries; }
    public int getMaxIdleConnections() { return maxIdleConnections; }
    public long getKeepAliveDuration() { return keepAliveDuration; }
    
    /**
     * Builder for PuxbayConfig.
     */
    public static class Builder {
        private final String apiKey;
        private String baseUrl = "https://api.puxbay.com/api/v1";
        private int timeout = 30;
        private int maxRetries = 3;
        private int maxIdleConnections = 10;
        private long keepAliveDuration = 300;
        
        /**
         * Creates a new builder with the required API key.
         *
         * @param apiKey Puxbay API key (must start with 'pb_')
         */
        public Builder(String apiKey) {
            this.apiKey = apiKey;
        }
        
        /**
         * Sets the base URL for the API.
         *
         * @param baseUrl Base URL
         * @return this builder
         */
        public Builder baseUrl(String baseUrl) {
            this.baseUrl = baseUrl;
            return this;
        }
        
        /**
         * Sets the request timeout in seconds.
         *
         * @param timeout Timeout in seconds
         * @return this builder
         */
        public Builder timeout(int timeout) {
            this.timeout = timeout;
            return this;
        }
        
        /**
         * Sets the maximum number of retry attempts.
         *
         * @param maxRetries Maximum retries
         * @return this builder
         */
        public Builder maxRetries(int maxRetries) {
            this.maxRetries = maxRetries;
            return this;
        }
        
        /**
         * Sets the maximum number of idle connections in the pool.
         *
         * @param maxIdleConnections Maximum idle connections
         * @return this builder
         */
        public Builder maxIdleConnections(int maxIdleConnections) {
            this.maxIdleConnections = maxIdleConnections;
            return this;
        }
        
        /**
         * Sets the keep-alive duration for connections in seconds.
         *
         * @param keepAliveDuration Keep-alive duration in seconds
         * @return this builder
         */
        public Builder keepAliveDuration(long keepAliveDuration) {
            this.keepAliveDuration = keepAliveDuration;
            return this;
        }
        
        /**
         * Builds the configuration.
         *
         * @return PuxbayConfig instance
         */
        public PuxbayConfig build() {
            return new PuxbayConfig(this);
        }
    }
}
