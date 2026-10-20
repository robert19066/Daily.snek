# Errors and rate limits

The SDK raises errors rather than turning failed requests into success-shaped return values.

## Automatic handling of HTTP 429

For a `429 Too Many Requests` response:

1. **GET requests** wait for the `Retry-After` header and retry up to three times by default.
2. If `Retry-After` is absent or not parseable, a short exponential delay is used.
3. If the retries are exhausted, `RateLimitError` is raised.
4. **POST, PUT, PATCH, and DELETE are not automatically retried.** This avoids repeating a write when the server's response does not tell us whether it had a side effect.

This default is bounded. A caller may catch `RateLimitError` and decide when a later operation is appropriate:

```python
from snek.rawFetch import RateLimitError

try:
    result = client.getPopularFeed()
except RateLimitError as error:
    print("Rate limit response:", error.response.status_code)
    if error.retry_after is not None:
        print(f"Retry manually in {error.retry_after:g} seconds.")
```

`RateLimitError` subclasses `requests.HTTPError`, exposes the original HTTP response through `.response`, and includes `.retry_after` in seconds as a suggested wait.

## Other failures

- Other HTTP error statuses raise `requests.HTTPError` via `raise_for_status()`.
- Connection and timeout failures raise the corresponding `requests.RequestException` subclasses.
- An unset `DAILY_DEV_KEY` raises `ValueError` when constructing `AutoApiToken`.

Catch only the error types your application can handle; allow unexpected failures to remain visible.

## Inspecting rate-limit headers

The helper methods `client.getRateLimit()`, `client.getRateRemaining()`, `client.getRateResetTime()`, and `client.getRetryTime()` read headers from the latest API response. They do not make additional API calls. Each returns a string or `None`.
