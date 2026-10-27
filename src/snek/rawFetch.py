from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import math
import time

import requests

from .errors import RateLimitError
from .tokenSys import AutoApiToken, ManualApiToken


class RawFetch:
    def __init__(
        self,
        token: ManualApiToken | AutoApiToken,
        max_rate_limit_retries: int = 3,
    ):
        if max_rate_limit_retries < 0:
            raise ValueError("max_rate_limit_retries must be zero or greater")

        self.token = token
        self.base_url = "https://api.daily.dev/public/v1"
        self.max_rate_limit_retries = max_rate_limit_retries
        self.last_response: requests.Response | None = None

    @staticmethod
    def _retry_after_seconds(response: requests.Response, attempt: int) -> float:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                seconds = float(retry_after)
                if math.isfinite(seconds):
                    return max(0.0, seconds)
            except ValueError:
                pass

            try:
                retry_time = parsedate_to_datetime(retry_after)
                if retry_time.tzinfo is None:
                    retry_time = retry_time.replace(tzinfo=timezone.utc)
                return max(
                    0.0,
                    (retry_time - datetime.now(timezone.utc)).total_seconds(),
                )
            except (TypeError, ValueError, OverflowError):
                pass

        return float(2**attempt)

    def get_rate_limit_header(self, name: str) -> str | None:
        """Read a rate-limit header from the most recent API response."""
        if self.last_response is None:
            return None
        return self.last_response.headers.get(name)

    def fetch(
        self,
        endpoint: str,
        method: str = "GET",
        params: dict | None = None,
        json: dict | list | None = None,
    ):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": "Bearer " + self.token.get_token(),
            "Accept": "application/json",
        }
        normalized_method = method.upper()
        attempts = 0

        while True:
            response = requests.request(
                method=normalized_method,
                url=url,
                headers=headers,
                params=params,
                json=json,
            )
            self.last_response = response

            if response.status_code == 429:
                retry_after = self._retry_after_seconds(response, attempts)
                if (
                    normalized_method != "GET"
                    or attempts >= self.max_rate_limit_retries
                ):
                    raise RateLimitError(response, retry_after)

                try:
                    time.sleep(retry_after)
                except OverflowError:
                    raise RateLimitError(response, retry_after) from None
                attempts += 1
                continue

            response.raise_for_status()
            if not response.content:
                return None
            return response.json()

    def get(self, endpoint: str, params: dict | None = None):
        return self.fetch(endpoint, method="GET", params=params)

    def post(
        self,
        endpoint: str,
        json: dict | list | None = None,
        params: dict | None = None,
    ):
        return self.fetch(endpoint, method="POST", params=params, json=json)

    def put(
        self,
        endpoint: str,
        json: dict | list | None = None,
        params: dict | None = None,
    ):
        return self.fetch(endpoint, method="PUT", params=params, json=json)

    def patch(
        self,
        endpoint: str,
        json: dict | list | None = None,
        params: dict | None = None,
    ):
        return self.fetch(endpoint, method="PATCH", params=params, json=json)

    def delete(
        self,
        endpoint: str,
        params: dict | None = None,
        json: dict | list | None = None,
    ):
        return self.fetch(endpoint, method="DELETE", params=params, json=json)
