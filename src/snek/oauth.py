import base64
from dataclasses import dataclass
import hashlib
import secrets
from urllib.parse import urlencode

import requests

PUBLIC_API_RESOURCE = "https://api.daily.dev/public/v1"
MCP_RESOURCE = "https://api.daily.dev/mcp"

AUTHORIZATION_ENDPOINT = "https://api.daily.dev/auth/oauth2/authorize"
TOKEN_ENDPOINT = "https://api.daily.dev/auth/oauth2/token"
REVOCATION_ENDPOINT = "https://api.daily.dev/auth/oauth2/revoke"

DEFAULT_OAUTH_SCOPES = "openid profile offline_access read write"


@dataclass(frozen=True)
class OAuthAuthorizationRequest:
    authorization_url: str
    code_verifier: str
    state: str


class OAuth2Client:
    """OAuth 2.1 authorization-code/PKCE helper for confidential server apps."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        resource: str = PUBLIC_API_RESOURCE,
    ):
        if not client_id:
            raise ValueError("client_id must not be empty")
        if not client_secret:
            raise ValueError("client_secret must not be empty")
        if resource not in (PUBLIC_API_RESOURCE, MCP_RESOURCE):
            raise ValueError(
                "resource must be the daily.dev Public API or MCP resource URL"
            )

        self.client_id = client_id
        self.client_secret = client_secret
        self.resource = resource

    def create_authorization_request(
        self,
        redirect_uri: str,
        scope: str = DEFAULT_OAUTH_SCOPES,
    ) -> OAuthAuthorizationRequest:
        code_verifier = secrets.token_urlsafe(32)
        code_challenge = (
            base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode("ascii")).digest()
            )
            .rstrip(b"=")
            .decode("ascii")
        )
        state = secrets.token_urlsafe(24)
        query = urlencode(
            {
                "response_type": "code",
                "client_id": self.client_id,
                "redirect_uri": redirect_uri,
                "scope": scope,
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
                "resource": self.resource,
            }
        )
        return OAuthAuthorizationRequest(
            authorization_url=f"{AUTHORIZATION_ENDPOINT}?{query}",
            code_verifier=code_verifier,
            state=state,
        )

    def exchange_code(
        self,
        code: str,
        redirect_uri: str,
        code_verifier: str,
    ) -> dict[str, object]:
        return self._post_token(
            {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code_verifier": code_verifier,
                "resource": self.resource,
            }
        )

    def refresh_access_token(self, refresh_token: str) -> dict[str, object]:
        return self._post_token(
            {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "resource": self.resource,
            }
        )

    def revoke_token(
        self,
        token: str,
        token_type_hint: str = "refresh_token",
    ) -> dict[str, object] | None:
        response = requests.post(
            REVOCATION_ENDPOINT,
            data={
                "token": token,
                "token_type_hint": token_type_hint,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )
        response.raise_for_status()
        if not response.content:
            return None
        return response.json()

    def _post_token(self, data: dict[str, str]) -> dict[str, object]:
        response = requests.post(TOKEN_ENDPOINT, data=data)
        response.raise_for_status()
        return response.json()
