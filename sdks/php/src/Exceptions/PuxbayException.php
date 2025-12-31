<?php

namespace Puxbay\Exceptions;

/**
 * Base exception for all Puxbay API errors.
 */
class PuxbayException extends \Exception
{
    protected int $statusCode;
    
    public function __construct(string $message, int $statusCode)
    {
        parent::__construct($message);
        $this->statusCode = $statusCode;
    }
    
    public function getStatusCode(): int
    {
        return $this->statusCode;
    }
}

class AuthenticationException extends PuxbayException {}
class RateLimitException extends PuxbayException {}
class ValidationException extends PuxbayException {}
class NotFoundException extends PuxbayException {}
class ServerException extends PuxbayException {}
