export class PuxbayError extends Error {
    constructor(
        message: string,
        public statusCode: number,
        public response?: any
    ) {
        super(message);
        this.name = 'PuxbayError';
    }
}

export class AuthenticationError extends PuxbayError {
    constructor(message: string, statusCode: number) {
        super(message, statusCode);
        this.name = 'AuthenticationError';
    }
}

export class RateLimitError extends PuxbayError {
    constructor(message: string, statusCode: number) {
        super(message, statusCode);
        this.name = 'RateLimitError';
    }
}

export class ValidationError extends PuxbayError {
    constructor(message: string, statusCode: number) {
        super(message, statusCode);
        this.name = 'ValidationError';
    }
}

export class NotFoundError extends PuxbayError {
    constructor(message: string, statusCode: number) {
        super(message, statusCode);
        this.name = 'NotFoundError';
    }
}

export class ServerError extends PuxbayError {
    constructor(message: string, statusCode: number) {
        super(message, statusCode);
        this.name = 'ServerError';
    }
}
