package com.puxbay.exceptions;

public class RateLimitException extends PuxbayException {
    public RateLimitException(String message, int statusCode) {
        super(message, statusCode);
    }
}
