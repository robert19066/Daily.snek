# Quickstart

## Create a client

Use `AutoApiToken` to read `DAILY_DEV_KEY` from the environment or a local `.env` file:

```python
from snek.snekSDK import SnekSDK
from snek.tokenSys import AutoApiToken

client = SnekSDK(AutoApiToken())
```

Or provide a token explicitly:

```python
from snek.snekSDK import SnekSDK
from snek.tokenSys import ManualApiToken

client = SnekSDK(ManualApiToken("your_daily_dev_api_token"))
```

`AutoApiToken()` raises `ValueError` immediately if `DAILY_DEV_KEY` is not set. This makes a missing credential visible instead of sending an unusable request.

## Fetch a feed

```python
posts = client.getPopularFeed()
print(posts)
```

The SDK returns decoded JSON for responses with a body, and `None` for a successful response without a body. Consult the daily.dev API response shape when consuming specific fields.

## Handle request errors

Non-success HTTP responses raise `requests.HTTPError` (or a more specific `requests` exception). A `429 Too Many Requests` response that cannot be resolved by automatic retries raises `RateLimitError`:

```python
from snek.rawFetch import RateLimitError
import requests

try:
    posts = client.getPopularFeed()
except RateLimitError as error:
    print("Rate limited; retry after:", error.retry_after)
except requests.HTTPError as error:
    print("The API returned an HTTP error:", error)
except requests.RequestException as error:
    print("The request failed before a successful response:", error)
```

See [Errors and rate limits](rate-limits.md) for retry rules and safe handling patterns.
