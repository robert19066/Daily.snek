# Quickstart

## Create a client

Use `AutoApiToken` to read `DAILY_DEV_KEY` from the environment or a local `.env` file:

```python
from snek import AutoApiToken, SnekSDK

client = SnekSDK(AutoApiToken())
```

Or provide a token explicitly:

```python
from snek import ManualApiToken, SnekSDK

client = SnekSDK(ManualApiToken("your_daily_dev_api_token"))
```

`AutoApiToken()` raises `ValueError` immediately if `DAILY_DEV_KEY` is not set. This makes a missing credential visible instead of sending an unusable request.

## Fetch a feed

```python
import json

posts = client.get_popular_feed()
print(json.dumps(posts, indent=2))
```

Prefer the Pythonic spelling `get_popular_feed()`; existing camelCase methods
remain available as compatibility aliases. The SDK returns decoded JSON for
responses with a body, and `None` for a successful response without a body.

For example, the result of a feed request has this response shape (the post and
cursor values vary):

```json
{
  "data": [
    {
      "id": "post-123",
      "title": "Building reliable Python services",
      "url": "https://example.com/python-services",
      "source": {
        "id": "source-1",
        "name": "Example Engineering",
        "handle": "example",
        "image": null
      },
      "tags": ["python"],
      "numUpvotes": 42,
      "numComments": 7
    }
  ],
  "pagination": {
    "hasNextPage": true,
    "cursor": "next-page-cursor"
  }
}
```

Pass the cursor back in the next request to fetch another page:

```python
next_page = client.get_popular_feed(
    params={"cursor": posts["pagination"]["cursor"]}
)
```

## Handle request errors

Non-success HTTP responses raise `requests.HTTPError` (or a more specific `requests` exception). A `429 Too Many Requests` response that cannot be resolved by automatic retries raises `RateLimitError`:

```python
from snek import RateLimitError
import requests

try:
    posts = client.get_popular_feed()
except RateLimitError as error:
    print("Rate limited; retry after:", error.retry_after)
except requests.HTTPError as error:
    print("The API returned an HTTP error:", error)
except requests.RequestException as error:
    print("The request failed before a successful response:", error)
```

See [Errors and rate limits](rate-limits.md) for retry rules and safe handling patterns.

For daily.dev OAuth app setup or MCP clients, see [OAuth and MCP](oauth-mcp.md).
