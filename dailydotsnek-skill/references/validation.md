# Validation checklist

- Confirm Python 3.10+ and `dailydotsnek` are installed.
- Confirm `DAILY_DEV_KEY` is supplied through a secret store, environment, or private `.env`.
- Exercise one read call and verify the result is decoded JSON or `None`.
- Verify missing credentials fail at `AutoApiToken()` construction.
- Verify code handles `RateLimitError`, `requests.HTTPError`, and `requests.RequestException` as appropriate.
- Do not automatically retry write methods.
- Check that rate-limit helpers are read after a request and are treated as `str | None`.
- Do not use `recommendSemantic` for new integrations.
- Never log tokens or include them in source control.
