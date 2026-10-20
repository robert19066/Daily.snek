# Changelog

All notable changes to this project are documented in this file.

## [1.1.0] - 2026-10-20
### Added
- Bounded retries for rate-limited GET requests, honoring `Retry-After`.
- A dedicated `RateLimitError` for rate-limit responses that cannot be retried.
- Documentation for authentication, SDK methods, exceptions, and rate limits.
### Fixed
- API requests now send the configured bearer token.
- Rate-limit helper methods now inspect the latest response instead of making API calls.
- Missing `DAILY_DEV_KEY` now fails clearly when creating `AutoApiToken`.

## [1.0.0] - 2026-10-13
### Added
- Initial public release
- Core SDK methods for feeds, posts, bookmarks, profile, and search
- Basic documentation and examples
