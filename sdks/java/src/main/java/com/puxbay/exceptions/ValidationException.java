package com.puxbay.exceptions;

public class ValidationException extends PuxbayException {
    public ValidationException(String message, int statusCode) {
        super(message, statusCode);
    }
}
