package com.puxbay.exceptions;

public class ServerException extends PuxbayException {
    public ServerException(String message, int statusCode) {
        super(message, statusCode);
    }
}
