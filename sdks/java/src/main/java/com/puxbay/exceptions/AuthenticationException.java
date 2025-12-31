package com.puxbay.exceptions;

public class AuthenticationException extends PuxbayException {
    public AuthenticationException(String message, int statusCode) {
        super(message, statusCode);
    }
}
