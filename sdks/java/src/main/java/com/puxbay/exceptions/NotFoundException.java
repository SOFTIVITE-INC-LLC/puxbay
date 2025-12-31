package com.puxbay.exceptions;

public class NotFoundException extends PuxbayException {
    public NotFoundException(String message, int statusCode) {
        super(message, statusCode);
    }
}
