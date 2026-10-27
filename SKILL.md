---
name: dailydotsnek-repository
description: Work on the Daily.snek repository, a Python 3.10+ SDK for daily.dev's public API, including API client methods, token handling, HTTP behavior, rate-limit retries, tests, documentation, packaging, and release automation.
---

# Daily.snek Repository Skill

## Purpose and scope

This skill is for AI coding agents working in [`robert19066/Daily.snek`](https://github.com/robert19066/Daily.snek), whose published Python distribution is named `dailydotsnek` and whose import package is `snek`.

The project is a small Python client for the daily.dev public API at `https://api.daily.dev/public/v1`. Its high-level SDK covers feeds, posts and comments, search, bookmarks, profile data, stack items, experiences, tags, recommendations, signup, and rate-limit header inspection. The low-level HTTP layer uses `requests`, attaches a bearer token, decodes JSON, raises HTTP errors, and retries HTTP 429 responses only for GET requests.

Use this document to navigate the code, make focused changes, validate behavior, and avoid accidental changes to release or publishing workflows. The repository's current source code is authoritative when it conflicts with documentation.

## Repository map

The default branch is `main`. The inspected recursive Git tree was not truncated.

```text
.
├── .github/
│   └── workflows/
│       └── release.yml
├── dailydotsnek-skill/
│   ├── SKILL.md
│   └── references/
│       ├── api.md
│       └── validation.md
├── docs/
│   ├── api.md
│   ├── changelog.md
│   ├── contributing.md
│   ├── index.md
│   ├── installation.md
│   ├── publishing.md
│   ├── rate-limits.md
│   └── usage.md
├── media/
│   └── Neon Daily.snek Snake Logo.png
├── src/
│   ├── __init__.py
│   └── snek/
│       ├── __init__.py
│       ├── errors.py
│       ├── rawFetch.py
│       ├── snekSDK.py
│       └── tokenSys.py
├── tests/
│   ├── test_rate_limit.py
│   └── test_release.py
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── map_src.py
├── mkdocs.yml
├── pyproject.toml
├── release.py
└── test.py
```

`test.py` is empty in the inspected tree. Tests currently live in `tests/`. Do not assume a test framework or test command beyond what is present in the repository; the checked-in tests use Python's `unittest`.

## Project configuration and setup

### Runtime and dependencies

`pyproject.toml` declares:

- Python `>=3.10`
- Distribution name: `dailydotsnek`
- Version at inspection: `1.3.0`
- Build backend: Hatchling
- Runtime dependencies: `requests>=2.31` and `python-dotenv>=1.0`

The wheel is configured to package `src/snek`. The source distribution includes the README, project configuration, `src/**`, `media/**`, `docs/**`, and `mkdocs.yml`.

Install the published package:

```bash
python -m pip install dailydotsnek
```

For local development from a checkout:

```bash
python -m pip install -e .
```

The package requires a daily.dev API token for authenticated API operations. Use a local `.env` file or an environment variable:

```dotenv
DAILY_DEV_KEY=your_daily_dev_api_token
```

Keep `.env` out of version control. Never log or commit API tokens.

Create a client using automatic environment loading:

```python
from snek.snekSDK import SnekSDK
from snek.tokenSys import AutoApiToken

client = SnekSDK(AutoApiToken())
posts = client.getPopularFeed()
```

Or provide a token explicitly:

```python
from snek.snekSDK import SnekSDK
from snek.tokenSys import ManualApiToken

client = SnekSDK(ManualApiToken(token))
```

`AutoApiToken()` calls `dotenv.load_dotenv()`, reads `DAILY_DEV_KEY` by default, and raises `ValueError` if the configured variable is missing or empty. It accepts a custom environment-variable name. `ManualApiToken` stores the supplied string without additional validation.

### Documentation preview

The documentation uses MkDocs Material. Install the docs dependency and serve locally:

```bash
python -m pip install mkdocs-material
python -m mkdocs serve
```

The navigation and Markdown extensions are configured in `mkdocs.yml`.

## Architecture and source responsibilities

### `src/snek/snekSDK.py`: public high-level client

`SnekSDK` accepts a `ManualApiToken` or `AutoApiToken`, stores it, sets the daily.dev public API base URL, and constructs a `RawFetch` instance. Public methods are thin wrappers mapping Python method names to API endpoints. Most methods return the decoded JSON payload unchanged.

Important rule: use the API's actual request and response contract. Do not invent payload keys for methods that accept `**data`, and do not silently reshape server responses unless a change explicitly requires it.

#### Method inventory

- Feeds: `getPersonalisedFeed()`, `getPopularFeed()`, `getDiscussedFeed()`, `getTagFeed(tag)`, `getSourceFeed(source)`
- Posts: `getPost(post_id)`, `getPostComments(post_id)`
- Search: `searchPosts(query)`, `searchTags(query)`, `searchSources(query)`, `getTags()`
- Recommendations: `recommendByKeyword(keyword)`, `recommendSemantic(**params)`
- Bookmarks: `getBookmarks()`, `addBookmarks(post_ids, list_id=None)`, `searchBookmarks(query)`, `getBookmarkLists()`, `createBookmarkList(name, icon=None)`, `deleteBookmarkList(list_id)`, `deleteBookmark(bookmark_id)`, `moveBookmark(bookmark_id, list_id)`
- Profile: `getProfile()`, `updateProfile(**data)`
- Stack: `searchStack(query)`, `getStack()`, `addStackItem(**data)`, `updateStackItem(item_id, **data)`, `deleteStackItem(item_id)`, `reorderStack(**data)`
- Experiences: `getExperiences()`, `createExperience(**data)`, `getExperience(experience_id)`, `updateExperience(experience_id, **data)`, `deleteExperience(experience_id)`
- Signup: `signup(**data)`
- Rate-limit header helpers: `getRateLimit()`, `getRateRemaining()`, `getRateResetTime()`, `getRetryTime()`

`recommendSemantic(**params)` is documented in the source as deprecated by daily.dev. Prefer `recommendByKeyword(keyword)` for new code.

### `src/snek/rawFetch.py`: HTTP transport and rate limits

`RawFetch` is the common transport used by `SnekSDK`.

- Base URL: `https://api.daily.dev/public/v1`
- Authentication: `Authorization: Bearer <token>`
- Accept header: `application/json`
- Supports query parameters and JSON bodies.
- Normalizes the HTTP method to uppercase.
- Stores the latest response in `last_response`.
- Uses `response.raise_for_status()` for non-429 HTTP failures.
- Returns `None` when a successful response has an empty body; otherwise returns `response.json()`.

The `fetch()` signature accepts `endpoint`, `method="GET"`, `params`, and `json`. It strips a leading slash from the endpoint before joining it to the base URL. Convenience methods `get`, `post`, `put`, `patch`, and `delete` delegate to `fetch`.

#### HTTP 429 retry contract

The default `max_rate_limit_retries` is `3`; negative values raise `ValueError`. This is the number of retries after the first attempt, so a GET may make up to four requests total when all attempts return 429.

For HTTP 429:

1. Parse `Retry-After` as a number of seconds when possible.
2. Otherwise, attempt to parse it as an HTTP date and calculate the non-negative delay.
3. If absent or invalid, use exponential fallback delays of `2**attempt` seconds.
4. Retry only when the method is `GET` and retries remain.
5. Raise `RateLimitError` for non-GET methods or after the retry budget is exhausted.

Do not automatically retry POST, PUT, PATCH, or DELETE. Their side effects may already have occurred even if the server returns a rate-limit response. Avoid wrapping writes in blind retry loops.

A `RateLimitError` includes the original response and a `retry_after` suggestion in seconds. An extreme sleep overflow is converted into `RateLimitError`. Other HTTP errors remain `requests.HTTPError` subclasses; network/timeout problems surface through `requests` exceptions.

Rate-limit helpers read the latest response's headers and do not make additional API calls. Before the first request, or if a header is missing, they return `None`. The SDK helper return type is effectively `str | None`.

### `src/snek/tokenSys.py`: credentials

- `ManualApiToken(token)` stores an explicitly supplied token.
- `AutoApiToken(apienvkeyname="DAILY_DEV_KEY")` loads `.env` values and reads the named environment variable.
- Missing automatic credentials raise `ValueError` during client-token construction, before the network request.

Do not introduce token logging, hard-coded credentials, or secret-bearing test fixtures. Tests should use clearly fake tokens.

### `src/snek/errors.py`: exception types

`RateLimitError` is the relevant, implemented exception used by `RawFetch`. It subclasses `requests.HTTPError` and stores `.retry_after`.

The file also contains `ServerDownError`, `NotFoundError`, and `CustomServerError`. Inspect and test these before relying on them: their current implementations appear incomplete and are not used by the primary request path. Prefer the actual exceptions raised by `RawFetch` unless deliberately fixing and testing these classes.

### `src/snek/__init__.py` and `src/__init__.py`

These package initializer files are generated/maintained in conjunction with `map_src.py`. Inspect generated exports before changing them manually; the generator discovers public top-level functions, classes, and uppercase constants using Python's AST and writes explicit `__all__` lists.

### `map_src.py`: package export generator

`map_src.py` walks the source tree, ignores common generated/virtual-environment directories, inspects Python modules with `ast`, and generates `__init__.py` files and `__all__` exports. It has a `--dry-run` option:

```bash
python map_src.py --dry-run
```

Without `--dry-run`, it writes generated initializer files. Review the output before running it on a working tree with changes. Public symbol detection is intentionally simple: top-level public functions/classes and uppercase assignments are exported; private names are excluded.

### `release.py`: interactive release preparation

`release.py` is a release utility, not a normal runtime module. It:

- Reads the static version from `pyproject.toml` and requires `MAJOR.MINOR.PATCH`.
- Generates package exports through `map_src.py`.
- Scans Python imports to help discover undeclared dependencies.
- Updates project dependencies and `CHANGELOG.md`.
- Collects a release summary, categorized notes, validation notes, and a commit title.
- Supports `--dry-run`.
- For a real release, requires a clean Git working tree, a named branch, and an `origin` remote.
- Builds wheel and source distributions, checks them with Twine, asks for confirmation before uploading to PyPI, then stages selected release files and commits/pushes.

**Caution:** a non-dry-run release can publish a package to the real PyPI index and push Git commits. Do not execute it as a casual validation step. Use `python release.py --dry-run` only when its interactive prompts are appropriate, and inspect the script/docs before any real publishing operation.

The version bump choices are `PATCH`, `MINOR`, `MEDIUM`, and `MAJOR`; `MEDIUM` is a legacy synonym for `MINOR`.

### `.github/workflows/release.yml`: GitHub Releases

The workflow runs on pushes to `main` and on manual dispatch. It extracts the latest version section from `CHANGELOG.md`, determines commits in the push range (or the selected commit for manual runs), and creates a GitHub Release for each commit. Release tags use the form `v<version>-commit-<12-character-sha>`. Existing tags are skipped. This workflow creates GitHub Releases; it is separate from `release.py`, which handles package publishing to PyPI.

## Testing and validation

The checked-in tests use `unittest` and mock HTTP calls rather than depending on live daily.dev API responses.

- `tests/test_rate_limit.py` verifies GET retry behavior, bearer-token headers, write non-retry behavior, retry exhaustion, ordinary HTTP errors, HTTP-date parsing, and rate-limit helper header names.
- `tests/test_release.py` verifies release-note collection and required summary, validation, and commit title prompts.
- `test.py` is empty in the inspected tree.

From the repository root, install the package in editable mode, then run:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

For a focused check:

```bash
python -m unittest tests.test_rate_limit -v
python -m unittest tests.test_release -v
```

If module-style test discovery fails due to package layout, use the `discover -s tests` command above. Tests should not call the live API; keep transport tests mocked.

For documentation changes, preview with `python -m mkdocs serve`. For packaging/release logic, inspect `docs/publishing.md` and the relevant release scripts before executing any publishing action.

## Coding and change conventions

1. **Keep the SDK thin.** Add high-level methods as clear endpoint wrappers; put shared HTTP behavior in `RawFetch`.
2. **Preserve return behavior.** Return decoded JSON unchanged or `None` for a successful empty response unless there is a deliberate, documented API change.
3. **Preserve safe retry semantics.** Never automatically replay write requests after HTTP 429.
4. **Use precise exception behavior.** Keep `RateLimitError` as an `HTTPError` subclass and retain the original response and retry delay.
5. **Use the API contract.** Confirm endpoint names, query parameters, and JSON payload fields against the daily.dev public API documentation. Do not infer write payload fields from method names alone.
6. **Keep secrets out of code.** Use `AutoApiToken`, `ManualApiToken`, environment variables, or a private `.env`; never commit credentials.
7. **Test with mocks.** Cover success, empty response, ordinary HTTP errors, 429 with numeric and date `Retry-After`, malformed/missing headers, retry exhaustion, and non-retried writes where relevant.
8. **Keep documentation aligned.** Update `docs/api.md`, `docs/usage.md`, or `docs/rate-limits.md` when public behavior changes. If the skill docs in `dailydotsnek-skill/` change, update its API/validation reference files as needed.
9. **Review generated files.** If source modules or public symbols change, inspect `map_src.py --dry-run` output before regenerating package exports.
10. **Treat publishing as a side effect.** Never run a real release, PyPI upload, or push without explicit user authorization and a review of the intended version, notes, artifacts, branch, and remote.

## Recommended workflow for an AI agent

1. Read `README.md` and the relevant guide in `docs/`.
2. Inspect the exact implementation in `src/snek/` before proposing a behavior change.
3. Identify whether the change belongs in the high-level wrapper (`snekSDK.py`), HTTP layer (`rawFetch.py`), token provider (`tokenSys.py`), exception module (`errors.py`), tests, or docs.
4. Check the current API contract before changing endpoints or request payloads.
5. Make the smallest coherent patch. Avoid unrelated formatting or generated-file churn.
6. Add or update mocked unit tests for observable behavior and edge cases.
7. Run `python -m unittest discover -s tests -v`.
8. For docs, run MkDocs locally if available. For export changes, inspect `python map_src.py --dry-run`.
9. Review `git diff` for secrets, accidental changes, generated artifacts, and release-related side effects.
10. Summarize changed behavior, tests run, and any unverified assumptions.

## Troubleshooting

- **`ValueError` from `AutoApiToken`:** confirm `DAILY_DEV_KEY` is set in the process environment or in a `.env` file in the current working directory; verify the variable name if a custom key was passed.
- **HTTP 401/403:** check token validity and whether the daily.dev API permits the requested endpoint. The SDK raises the API's HTTP error rather than silently recovering.
- **HTTP 429 / `RateLimitError`:** inspect `.retry_after` and `.response`; GET calls have bounded automatic retries, writes do not.
- **Other HTTP status errors:** inspect the attached response and status code; `raise_for_status()` preserves standard `requests` behavior.
- **Connection or timeout failure:** handle the relevant `requests.RequestException` subclass at the application boundary.
- **Missing import/package issues in a checkout:** verify editable installation and inspect generated `src/snek/__init__.py` exports.
- **Documentation preview fails:** install `mkdocs-material` in the active Python environment and run `python -m mkdocs serve` from the project root.
- **Release command refuses to proceed:** inspect the error, Git working-tree status, current branch, configured `origin`, project version, and changelog. Do not bypass the safety checks without understanding their purpose.

## Repository sources inspected

The skill is based on the following files and repository metadata:

- [`README.md`](https://github.com/robert19066/Daily.snek/blob/main/README.md)
- [`pyproject.toml`](https://github.com/robert19066/Daily.snek/blob/main/pyproject.toml)
- [`src/snek/snekSDK.py`](https://github.com/robert19066/Daily.snek/blob/main/src/snek/snekSDK.py)
- [`src/snek/rawFetch.py`](https://github.com/robert19066/Daily.snek/blob/main/src/snek/rawFetch.py)
- [`src/snek/tokenSys.py`](https://github.com/robert19066/Daily.snek/blob/main/src/snek/tokenSys.py)
- [`src/snek/errors.py`](https://github.com/robert19066/Daily.snek/blob/main/src/snek/errors.py)
- [`src/snek/__init__.py`](https://github.com/robert19066/Daily.snek/blob/main/src/snek/__init__.py)
- [`map_src.py`](https://github.com/robert19066/Daily.snek/blob/main/map_src.py)
- [`release.py`](https://github.com/robert19066/Daily.snek/blob/main/release.py)
- [`tests/test_rate_limit.py`](https://github.com/robert19066/Daily.snek/blob/main/tests/test_rate_limit.py)
- [`tests/test_release.py`](https://github.com/robert19066/Daily.snek/blob/main/tests/test_release.py)
- [`docs/api.md`](https://github.com/robert19066/Daily.snek/blob/main/docs/api.md)
- [`docs/usage.md`](https://github.com/robert19066/Daily.snek/blob/main/docs/usage.md)
- [`docs/installation.md`](https://github.com/robert19066/Daily.snek/blob/main/docs/installation.md)
- [`docs/rate-limits.md`](https://github.com/robert19066/Daily.snek/blob/main/docs/rate-limits.md)
- [`docs/publishing.md`](https://github.com/robert19066/Daily.snek/blob/main/docs/publishing.md)
- [`docs/contributing.md`](https://github.com/robert19066/Daily.snek/blob/main/docs/contributing.md)
- [`mkdocs.yml`](https://github.com/robert19066/Daily.snek/blob/main/mkdocs.yml)
- [`.github/workflows/release.yml`](https://github.com/robert19066/Daily.snek/blob/main/.github/workflows/release.yml)
- [`dailydotsnek-skill/SKILL.md`](https://github.com/robert19066/Daily.snek/blob/main/dailydotsnek-skill/SKILL.md)
- [`dailydotsnek-skill/references/api.md`](https://github.com/robert19066/Daily.snek/blob/main/dailydotsnek-skill/references/api.md)
- [`dailydotsnek-skill/references/validation.md`](https://github.com/robert19066/Daily.snek/blob/main/dailydotsnek-skill/references/validation.md)
- [`CHANGELOG.md`](https://github.com/robert19066/Daily.snek/blob/main/CHANGELOG.md)
- [`CONTRIBUTING.md`](https://github.com/robert19066/Daily.snek/blob/main/CONTRIBUTING.md)
- [`LICENSE`](https://github.com/robert19066/Daily.snek/blob/main/LICENSE)

The recursive Git tree was inspected successfully and reported `truncated: false`. The binary logo asset was inventoried but not opened. `.gitignore` was inventoried but not analyzed line by line. Repository metadata showed a public Python repository on `main`, with MIT licensing and three open issues at the time of inspection. The live API, external daily.dev service behavior, package installation, tests, documentation build, and release workflow were not executed as part of this repository inspection.
