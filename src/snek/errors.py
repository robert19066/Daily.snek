from typing import Any

import requests

"""
Some useful exceptions. BETA FOR NOW!
"""

class RateLimitError(requests.HTTPError):
    """Raised when the API rate limit is reached and the request cannot be retried."""

    def __init__(self, response: requests.Response, retry_after: float | None):
        self.retry_after = retry_after
        wait_message = (
            f" Retry after {retry_after:g} seconds."
            if retry_after is not None
            else ""
        )
        super().__init__(
            f"Daily.dev API rate limit reached (HTTP 429).{wait_message}",
            response=response,
        )

class ServerDownError(requests.exceptions.HTTPError):
    def __init__(self, response=None, message=None) -> None:
        self.status_code = 502
        self.response
        msg = message or f"Server down, 502 bad gateway"

class NotFoundError(requests.exceptions.HTTPError):
    def __init__(self, response=None, message=None) -> None:
            self.status_code = 404
            self.response
            msg = message or f"Address not found, 404 not found."

class CustomServerError(requests.exceptions.HTTPError):
    def __init__(self, error: int = 000, description: str = "No description was provided") -> None:
            self.status_code = error
            self.description = description
            msg = f"Error Code {self.status_code}, {self.description}"