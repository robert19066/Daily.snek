import json
import unittest
from unittest.mock import Mock, patch

import requests

from snek.rawFetch import RateLimitError, RawFetch
from snek.snekSDK import SnekSDK
from snek.tokenSys import ManualApiToken


def make_response(status_code, *, headers=None, payload=None):
    response = requests.Response()
    response.status_code = status_code
    response.headers.update(headers or {})
    response.url = "https://api.daily.dev/public/v1/feeds/popular"
    response._content = (
        json.dumps(payload).encode("utf-8") if payload is not None else b""
    )
    return response


class RateLimitTests(unittest.TestCase):
    def test_get_retries_after_429_and_uses_bearer_token(self):
        rate_limited = make_response(429, headers={"Retry-After": "2"})
        success = make_response(
            200,
            headers={"x-ratelimit-remaining": "17"},
            payload={"items": []},
        )
        request = Mock(side_effect=[rate_limited, success])
        token = ManualApiToken("test-token")

        with (
            patch("requests.request", request),
            patch("snek.rawFetch.time.sleep") as sleep,
        ):
            client = RawFetch(token)
            result = client.get("feeds/popular")

        self.assertEqual(result, {"items": []})
        self.assertEqual(request.call_count, 2)
        self.assertEqual(
            request.call_args.kwargs["headers"]["Authorization"],
            f"Bearer {token.get_token()}",
        )
        sleep.assert_called_once_with(2.0)
        self.assertEqual(
            client.get_rate_limit_header("x-ratelimit-remaining"),
            "17",
        )

    def test_write_request_is_not_retried(self):
        response = make_response(429, headers={"Retry-After": "1"})
        request = Mock(return_value=response)

        with (
            patch("requests.request", request),
            patch("snek.rawFetch.time.sleep") as sleep,
        ):
            client = RawFetch(ManualApiToken("test-token"))
            with self.assertRaises(RateLimitError) as raised:
                client.post("bookmarks/", json={"postIds": ["post-1"]})

        self.assertIs(raised.exception.response, response)
        self.assertEqual(raised.exception.retry_after, 1.0)
        request.assert_called_once()
        sleep.assert_not_called()

    def test_get_raises_after_configured_retry_count(self):
        response = make_response(429, headers={"Retry-After": "0"})
        request = Mock(return_value=response)

        with (
            patch("requests.request", request),
            patch("snek.rawFetch.time.sleep"),
        ):
            client = RawFetch(
                ManualApiToken("test-token"),
                max_rate_limit_retries=2,
            )
            with self.assertRaises(RateLimitError):
                client.get("feeds/popular")

        self.assertEqual(request.call_count, 3)

    def test_non_rate_limit_http_errors_keep_requests_exception(self):
        response = make_response(500)

        with patch("requests.request", Mock(return_value=response)):
            client = RawFetch(ManualApiToken("test-token"))
            with self.assertRaises(requests.HTTPError):
                client.get("feeds/popular")

    def test_retry_after_http_date_is_parsed(self):
        response = make_response(
            429,
            headers={"Retry-After": "Wed, 21 Oct 2099 07:28:00 GMT"},
        )

        seconds = RawFetch._retry_after_seconds(response, attempt=0)

        self.assertGreater(seconds, 0)

    def test_sdk_rate_limit_helpers_read_headers_without_requests(self):
        client = SnekSDK(ManualApiToken("test-token"))
        with patch.object(
            client.fetch,
            "get_rate_limit_header",
            side_effect=["100", "42", "12345", None],
        ) as get_header:
            self.assertEqual(client.getRateLimit(), "100")
            self.assertEqual(client.getRateRemaining(), "42")
            self.assertEqual(client.getRateResetTime(), "12345")
            self.assertIsNone(client.getRetryTime())

        self.assertEqual(
            [call.args[0] for call in get_header.call_args_list],
            [
                "x-ratelimit-limit",
                "x-ratelimit-remaining",
                "x-ratelimit-reset",
                "retry-after",
            ],
        )


if __name__ == "__main__":
    unittest.main()
