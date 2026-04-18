"""Typed exceptions for the Tableau MCP server."""

from __future__ import annotations


class TableauError(Exception):
    """Base exception for all Tableau MCP errors."""


class AuthenticationError(TableauError):
    """Raised when PAT sign-in fails or the session is rejected."""


class APIError(TableauError):
    """Raised for non-2xx responses from the Tableau REST API."""

    def __init__(self, message: str, status_code: int | None = None, body: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class NotFoundError(APIError):
    """Raised when a Tableau resource (404) is not found."""
