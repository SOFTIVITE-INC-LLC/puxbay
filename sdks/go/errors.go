package puxbay

import (
	"encoding/json"
	"fmt"
)

// PuxbayError represents a Puxbay API error
type PuxbayError struct {
	StatusCode int
	Message    string
	Detail     string
}

func (e *PuxbayError) Error() string {
	if e.Detail != "" {
		return fmt.Sprintf("puxbay error (status %d): %s - %s", e.StatusCode, e.Message, e.Detail)
	}
	return fmt.Sprintf("puxbay error (status %d): %s", e.StatusCode, e.Message)
}

// AuthenticationError is returned when API key authentication fails
type AuthenticationError struct {
	*PuxbayError
}

// RateLimitError is returned when rate limit is exceeded
type RateLimitError struct {
	*PuxbayError
}

// ValidationError is returned when request validation fails
type ValidationError struct {
	*PuxbayError
}

// NotFoundError is returned when a resource is not found
type NotFoundError struct {
	*PuxbayError
}

// ServerError is returned when the server returns a 5xx error
type ServerError struct {
	*PuxbayError
}

// handleErrorResponse creates appropriate error types based on HTTP status code
func handleErrorResponse(statusCode int, body []byte) error {
	var errorResp struct {
		Detail  string `json:"detail"`
		Message string `json:"message"`
	}

	_ = json.Unmarshal(body, &errorResp)

	message := errorResp.Detail
	if message == "" {
		message = errorResp.Message
	}
	if message == "" {
		message = "unknown error"
	}

	baseErr := &PuxbayError{
		StatusCode: statusCode,
		Message:    message,
	}

	switch statusCode {
	case 401:
		return &AuthenticationError{PuxbayError: baseErr}
	case 429:
		return &RateLimitError{PuxbayError: baseErr}
	case 400:
		return &ValidationError{PuxbayError: baseErr}
	case 404:
		return &NotFoundError{PuxbayError: baseErr}
	default:
		if statusCode >= 500 {
			return &ServerError{PuxbayError: baseErr}
		}
		return baseErr
	}
}
