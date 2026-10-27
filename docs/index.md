# dailydotsnek

**A compact, approachable Python client for the daily.dev public API.**

Get useful API responses with a small client, familiar Python exceptions, and respectful handling of rate limits.

[:material-download: Install from PyPI](installation.md){ .md-button .md-button--primary }
[:material-rocket-launch: Make your first request](usage.md){ .md-button }

## Made for everyday use

| Capability | What you get |
| --- | --- |
| **Straightforward client** | One `SnekSDK` instance provides access to the API's main endpoint groups. |
| **Simple authentication** | Load `DAILY_DEV_KEY` from your environment or pass a token explicitly. |
| **Rate-limit-aware reads** | Retry GET requests using the server's `Retry-After` guidance, with a bounded retry count. |
| **Predictable errors** | HTTP failures remain exceptions; rate-limit exhaustion raises `RateLimitError`. |
| **Modern Python** | Supports Python 3.10 and later. |

## In three steps

Install the package:

```console
python -m pip install dailydotsnek
```

Set your `DAILY_DEV_KEY` environment variable (or add it to a local `.env` file), then:

```python
from snek import AutoApiToken, SnekSDK

client = SnekSDK(AutoApiToken())
posts = client.get_popular_feed()
print(posts)
```

> **Protect your token.** Never commit API credentials to a repository or paste them into logs.

## Explore

- [Installation and authentication](installation.md)
- [Quickstart, examples, and exceptions](usage.md)
- [SDK method reference](api.md)
- [OAuth apps and MCP integration](oauth-mcp.md)
- [Rate-limit behavior](rate-limits.md)

The source repository includes additional project guidance for [contributing](contributing.md), [releases](publishing.md), and the [changelog](changelog.md).
