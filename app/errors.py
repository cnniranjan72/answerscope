"""Structured application errors, rendered as {"error": {code, message, details}}."""
from __future__ import annotations

from typing import Any


class AppError(Exception):
    status_code = 400
    code = "bad_request"

    def __init__(self, message: str, details: Any = None, *, code: str | None = None):
        super().__init__(message)
        self.message = message
        self.details = details
        if code:
            self.code = code


class NotFound(AppError):
    status_code = 404
    code = "not_found"


class Unauthenticated(AppError):
    status_code = 401
    code = "unauthenticated"


class Forbidden(AppError):
    status_code = 403
    code = "forbidden"


class Conflict(AppError):
    """Request is well-formed but conflicts with current state (stale version, invalid transition)."""
    status_code = 409
    code = "conflict"


class Unprocessable(AppError):
    status_code = 422
    code = "validation_failed"
