package com.puxbay.exceptions;

/**
 * Base exception for all Puxbay API errors.
 */
public class PuxbayException extends Exception {
    private final int statusCode;
    
    public PuxbayException(String message, int statusCode) {
        super(message);
        this.statusCode = statusCode;
    }
    
    public int getStatusCode() {
        return statusCode;
    }
}
