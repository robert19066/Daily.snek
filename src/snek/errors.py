import requests


class RateLimitError(requests.HTTPError):
    """Raised when the API rate limit is reached and the request cannot be retried."""

    def __init__(self, response: requests.Response, retry_after: float | None):
        self.retry_after = retry_after
        wait_message = (
            f" Retry after {retry_after:g} seconds." if retry_after is not None else ""
        )
        super().__init__(
            f"Daily.dev API rate limit reached (HTTP 429).{wait_message}",
            response=response,
        )


class ServerDownError(requests.HTTPError):
    def __init__(
        self,
        response: requests.Response | None = None,
        message: str | None = None,
    ) -> None:
        self.status_code = 502
        super().__init__(
            message or "Server down, 502 bad gateway",
            response=response,
        )


class NotFoundError(requests.HTTPError):
    def __init__(
        self,
        response: requests.Response | None = None,
        message: str | None = None,
    ) -> None:
        self.status_code = 404
        super().__init__(
            message or "Address not found, 404 not found.",
            response=response,
        )


class CustomServerError(requests.HTTPError):
    def __init__(
        self,
        error: int = 0,
        description: str = "No description was provided",
    ) -> None:
        self.status_code = error
        self.description = description
        super().__init__(f"Error Code {self.status_code}, {self.description}")
