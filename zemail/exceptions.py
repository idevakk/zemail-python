from typing import Any, Dict, Optional


class ZemailError(Exception):
    """Base exception for all Zemail SDK errors."""

    pass


class ZemailAPIError(ZemailError):
    """
    Raised when the API returns an error response.
    """

    def __init__(
        self,
        message: str,
        type: str,
        code: str,
        status: int,
        param: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.type = type
        self.code = code
        self.status = status
        self.param = param
        self.request_id = request_id

    def __str__(self) -> str:
        s = f"{self.status} {self.type}: {self.message} (code: {self.code})"
        if self.param:
            s += f", param: {self.param}"
        if self.request_id:
            s += f", request_id: {self.request_id}"
        return s


class AuthenticationError(ZemailAPIError):
    """Raised for authentication errors (401)."""

    pass


class PermissionError(ZemailAPIError):
    """Raised for permission errors (403)."""

    pass


class NotFoundError(ZemailAPIError):
    """Raised when a resource is not found (404)."""

    pass


class InvalidRequestError(ZemailAPIError):
    """Raised for invalid requests (400, 422)."""

    pass


class ValidationError(InvalidRequestError):
    """Raised for validation failures (422) with a validation_failed code."""

    def __init__(
        self,
        message: str,
        code: str,
        status: int,
        param: Optional[str] = None,
        request_id: Optional[str] = None,
        errors: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "invalid_request_error", code, status, param, request_id)
        self.errors = errors or {}


class RateLimitError(ZemailAPIError):
    """Raised when rate limits are exceeded (429)."""

    pass
