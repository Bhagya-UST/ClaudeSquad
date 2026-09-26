"""
Standard error handling for ReturnIQ API
"""

from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional, Dict
import json

class ReturnIQError(HTTPException):
    """Base exception for ReturnIQ errors"""

    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict] = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}

        detail = {
            "error_code": error_code,
            "message": message,
            "details": self.details,
            "timestamp": datetime.utcnow().isoformat()
        }

        super().__init__(status_code=status_code, detail=detail)

# Validation Errors (400)
class ValidationError(ReturnIQError):
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            error_code="VALIDATION_ERROR",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )

class InvalidInputError(ReturnIQError):
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(
            error_code="INVALID_INPUT",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )

# Authentication Errors (401)
class AuthenticationError(ReturnIQError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            error_code="AUTHENTICATION_FAILED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class TokenExpiredError(ReturnIQError):
    def __init__(self):
        super().__init__(
            error_code="TOKEN_EXPIRED",
            message="Authentication token has expired",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class InvalidTokenError(ReturnIQError):
    def __init__(self):
        super().__init__(
            error_code="INVALID_TOKEN",
            message="Invalid authentication token",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

# Authorization Errors (403)
class AuthorizationError(ReturnIQError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            error_code="AUTHORIZATION_FAILED",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )

# Not Found Errors (404)
class NotFoundError(ReturnIQError):
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            error_code="NOT_FOUND",
            message=f"{resource_type} '{resource_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )

class ReturnNotFoundError(NotFoundError):
    def __init__(self, return_id: str):
        super().__init__("Return", return_id)

class TrendNotFoundError(NotFoundError):
    def __init__(self, trend_id: str):
        super().__init__("Trend", trend_id)

class RecommendationNotFoundError(NotFoundError):
    def __init__(self, rec_id: str):
        super().__init__("Recommendation", rec_id)

# Rate Limit Errors (429)
class RateLimitError(ReturnIQError):
    def __init__(self, retry_after: int = 60):
        super().__init__(
            error_code="RATE_LIMIT_EXCEEDED",
            message=f"Rate limit exceeded. Retry after {retry_after} seconds",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after": retry_after}
        )

# Server Errors (500)
class InternalServerError(ReturnIQError):
    def __init__(self, message: str = "Internal server error", error_id: Optional[str] = None):
        details = {"error_id": error_id} if error_id else {}
        super().__init__(
            error_code="INTERNAL_ERROR",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )

class DatabaseError(InternalServerError):
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message)

class LLMError(InternalServerError):
    def __init__(self, message: str = "LLM API call failed"):
        super().__init__(message)

class ProcessingError(InternalServerError):
    def __init__(self, message: str = "Failed to process request"):
        super().__init__(message)

# Convenience functions
def handle_error(error: Exception) -> ReturnIQError:
    """Convert generic exceptions to ReturnIQError"""
    if isinstance(error, ReturnIQError):
        return error

    return InternalServerError(
        message=str(error),
        error_id=getattr(error, 'error_id', None)
    )
