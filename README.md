<p align="center">
  <img src="media/Neon%20Daily.snek%20Snake%20Logo.png" alt="Daily.snek — a Python client for the daily.dev API" width="720">
</p>

<h1 align="center">dailydotsnek</h1>

<p align="center">
  A small, friendly Python client for the daily.dev public API.
  <br>
  Feeds, posts, bookmarks, profile tools, and search — with rate-limit-aware GET retries.
</p>

<p align="center">
  <a href="https://pypi.org/project/dailydotsnek/"><img src="https://img.shields.io/pypi/v/dailydotsnek?color=22c55e&label=PyPI" alt="PyPI version"></a>
  <img src="https://img.shields.io/pypi/pyversions/dailydotsnek?color=22c55e" alt="Supported Python versions">
</p>

## Get started

```powershell
python -m pip install dailydotsnek
```

The SDK requires Python 3.10 or later. It installs its HTTP and `.env` dependencies automatically.

## Your first request

Create a `.env` file in your project directory:

```dotenv
DAILY_DEV_KEY=your_daily_dev_api_token
```

Keep this file private: do not commit API tokens to source control.

```python
from snek.snekSDK import SnekSDK
from snek.tokenSys import AutoApiToken

client = SnekSDK(AutoApiToken())
popular_posts = client.getPopularFeed()

print(popular_posts)
print("Remaining requests:", client.getRateRemaining())
```

Prefer explicit secret management? Pass the token directly:

```python
from snek.snekSDK import SnekSDK
from snek.tokenSys import ManualApiToken

client = SnekSDK(ManualApiToken("your_daily_dev_api_token"))
```

## Rate limits, handled thoughtfully

When daily.dev returns HTTP `429 Too Many Requests`, the SDK automatically waits for the server's `Retry-After` value and retries **GET** requests up to three times. If the header is missing or invalid, it uses a short exponential delay. It does not automatically replay POST, PUT, PATCH, or DELETE requests, so a write is never silently duplicated.

If a request still cannot proceed, the SDK raises `RateLimitError`, a `requests.HTTPError` subclass. It includes the original response and a suggested `retry_after` wait:

```python
from snek.rawFetch import RateLimitError

try:
    posts = client.getPopularFeed()
except RateLimitError as error:
    print(f"Rate limit reached. Try again in {error.retry_after} seconds.")
```

Rate-limit helpers report headers from the most recent API response. They return `None` before the first request or when that response did not include the requested header.

## What’s included

| Area | Examples |
| --- | --- |
| Feeds | Personalized, popular, discussed, tag, and source feeds |
| Posts | Retrieve posts and their comments |
| Search | Search posts, tags, and sources |
| Bookmarks | Manage bookmarks and bookmark lists |
| Profile | Read and update your profile, stack, and experiences |
| API utilities | Tags, keyword recommendations, rate-limit headers |

## Documentation

Explore the [full documentation](docs/index.md), including the [installation guide](docs/installation.md), [quickstart and error handling](docs/usage.md), [API reference](docs/api.md), and [publishing guide](docs/publishing.md).

To preview the documentation site locally:

```powershell
python -m pip install mkdocs-material
python -m mkdocs serve
```
