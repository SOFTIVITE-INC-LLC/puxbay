using System;

namespace Puxbay.SDK.Exceptions
{
    /// <summary>
    /// Base exception for all Puxbay API errors.
    /// </summary>
    public class PuxbayException : Exception
    {
        /// <summary>
        /// Gets the HTTP status code.
        /// </summary>
        public int StatusCode { get; }
        
        public PuxbayException(string message, int statusCode) : base(message)
        {
            StatusCode = statusCode;
        }
    }
    
    /// <summary>
    /// Exception thrown when API key authentication fails.
    /// </summary>
    public class AuthenticationException : PuxbayException
    {
        public AuthenticationException(string message, int statusCode) : base(message, statusCode) { }
    }
    
    /// <summary>
    /// Exception thrown when rate limit is exceeded.
    /// </summary>
    public class RateLimitException : PuxbayException
    {
        public RateLimitException(string message, int statusCode) : base(message, statusCode) { }
    }
    
    /// <summary>
    /// Exception thrown when request validation fails.
    /// </summary>
    public class ValidationException : PuxbayException
    {
        public ValidationException(string message, int statusCode) : base(message, statusCode) { }
    }
    
    /// <summary>
    /// Exception thrown when a resource is not found.
    /// </summary>
    public class NotFoundException : PuxbayException
    {
        public NotFoundException(string message, int statusCode) : base(message, statusCode) { }
    }
    
    /// <summary>
    /// Exception thrown when the server returns a 5xx error.
    /// </summary>
    public class ServerException : PuxbayException
    {
        public ServerException(string message, int statusCode) : base(message, statusCode) { }
    }
}
