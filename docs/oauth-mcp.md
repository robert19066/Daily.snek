# OAuth and MCP

## OAuth 2.1 for Public API integrations

Use the OAuth helper when your server-side application acts on behalf of other
daily.dev users. OAuth apps use the authorization-code flow with PKCE. The
client secret must stay on your server; do not put it in a browser or mobile
application.

Register an OAuth app in daily.dev settings and configure its exact redirect
URI. Keep `DAILY_DEV_CLIENT_ID` and `DAILY_DEV_CLIENT_SECRET` in a secret
manager or environment variables.

```python
import os

from snek import OAuth2Client

oauth = OAuth2Client(
    client_id=os.environ["DAILY_DEV_CLIENT_ID"],
    client_secret=os.environ["DAILY_DEV_CLIENT_SECRET"],
)

authorization = oauth.create_authorization_request(
    redirect_uri="https://example.com/oauth/callback",
)

# Keep both values in the user's server-side session.
session["daily_dev_oauth_state"] = authorization.state
session["daily_dev_code_verifier"] = authorization.code_verifier
redirect_to(authorization.authorization_url)
```

At the callback, compare the returned `state` with the session value before
exchanging the code. The SDK returns the state and verifier to your app; your
web framework remains responsible for validating state, handling denial, and
securely storing tokens.

```python
from snek import ManualApiToken, SnekSDK

tokens = oauth.exchange_code(
    code=callback_query["code"],
    redirect_uri="https://example.com/oauth/callback",
    code_verifier=session["daily_dev_code_verifier"],
)

api = SnekSDK(ManualApiToken(tokens["access_token"]))
feed = api.get_personalised_feed()
```

Request only the scopes the application needs. The default scope is
`openid profile offline_access read write`; users can decline write access, so
handle an HTTP 403 insufficient-scope response. If you request
`offline_access`, store the newest refresh token after every rotation:

```python
tokens = oauth.refresh_access_token(refresh_token)
refresh_token = tokens["refresh_token"]
```

Revoke credentials when a user disconnects:

```python
oauth.revoke_token(refresh_token)
```

`OAuth2Client` raises the underlying `requests` exceptions for token endpoint
errors. Access tokens are resource-specific: the default resource is
`https://api.daily.dev/public/v1`. Use
`OAuth2Client(..., resource=MCP_RESOURCE)` only when your server-side
integration is obtaining an MCP-scoped token. REST tokens and MCP tokens are
not interchangeable.

See daily.dev's [OAuth app guide](https://docs.daily.dev/oauth-apps/) for app
registration, endpoint details, scopes, token lifetimes, and current error
semantics.

## Connect an MCP client

daily.dev also provides a hosted Streamable HTTP MCP server at
`https://api.daily.dev/mcp`. You do not need to install or run an MCP server
locally. Add the URL to an MCP-compatible client and complete the daily.dev
OAuth consent flow when prompted.

For example, VS Code's `.vscode/mcp.json` can register the remote server:

```json
{
  "servers": {
    "daily.dev": {
      "type": "http",
      "url": "https://api.daily.dev/mcp"
    }
  }
}
```

The server exposes Public API operations as tools. Read tools require `read`;
account-changing tools require `write`. MCP tool calls use the same account
quota as REST API calls, and Plus raises the available quota.

For other clients and current setup options, see the official
[daily.dev MCP server guide](https://docs.daily.dev/mcp-server/). Personal
access tokens are supported by some MCP clients for personal use, but OAuth is
recommended for applications used by other people. Never commit a token or
send it to a host other than `api.daily.dev`.

The Python SDK is a REST client and does not implement the MCP transport
protocol. Use an MCP-capable host for `https://api.daily.dev/mcp`; use
`SnekSDK` for direct Python REST calls.
