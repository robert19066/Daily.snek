---
name: dailydotsnek
description: Use the dailydotsnek Python client to call the daily.dev public API for feeds, posts, search, bookmarks, profile data, stack, experiences, tags, recommendations, and signup.
---

# dailydotsnek

Use this skill when writing or troubleshooting Python code that uses the `dailydotsnek` package. The package requires Python 3.10+ and exposes the client through `snek.snekSDK`.

## Setup

Install it with:

```bash
python -m pip install dailydotsnek
```

Use one of the verified token providers:

```python
from snek.snekSDK import SnekSDK
from snek.tokenSys import AutoApiToken

client = SnekSDK(AutoApiToken())
```

`AutoApiToken()` loads `DAILY_DEV_KEY` from the process environment or a local `.env` file and raises `ValueError` if it is missing. For explicit secret injection:

```python
from snek.tokenSys import ManualApiToken
client = SnekSDK(ManualApiToken(token))
```

Never commit, print, or expose the token.

## Core usage

Use the high-level methods listed in [references/api.md](references/api.md). They return decoded JSON, or `None` for a successful response with no body. Write-method keyword arguments are passed as JSON to the API; do not invent payload fields—use the daily.dev endpoint contract.

```python
posts = client.getPopularFeed()
post = client.getPost(post_id)
matches = client.searchPosts("python")
```

`recommendSemantic(**params)` is deprecated by daily.dev; prefer `recommendByKeyword(keyword)`.

## Errors and rate limits

Catch `snek.rawFetch.RateLimitError` for an exhausted HTTP 429 retry sequence, `requests.HTTPError` for other HTTP failures, and `requests.RequestException` for transport failures:

```python
from snek.rawFetch import RateLimitError
import requests

try:
    result = client.getPopularFeed()
except RateLimitError as error:
    # error.response is the original response; error.retry_after may be None.
    raise RuntimeError(f"Rate limited; retry after {error.retry_after}") from error
except requests.HTTPError:
    raise
except requests.RequestException:
    raise
```

HTTP 429 responses are retried automatically only for GET requests, up to three retries by default. The client uses `Retry-After` when valid and otherwise a short exponential delay. POST, PUT, PATCH, and DELETE are never automatically replayed. Do not add an outer automatic retry around writes unless the caller has an idempotency strategy.

After a request, `getRateLimit()`, `getRateRemaining()`, `getRateResetTime()`, and `getRetryTime()` read headers from the most recent response without making another request; each returns a string or `None`.

## Verification

Before publishing code that uses this skill, run the checks in [references/validation.md](references/validation.md). If documentation conflicts with implementation, treat the current source behavior as authoritative and call out the discrepancy.
