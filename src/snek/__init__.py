"""Automatically generated package exports."""

from .errors import CustomServerError, NotFoundError, RateLimitError, ServerDownError
from .oauth import (
    DEFAULT_OAUTH_SCOPES,
    MCP_RESOURCE,
    PUBLIC_API_RESOURCE,
    OAuth2Client,
    OAuthAuthorizationRequest,
)
from .rawFetch import RawFetch
from .snekSDK import SnekSDK
from .tokenSys import AutoApiToken, ManualApiToken

__all__ = [
    "AutoApiToken",
    "CustomServerError",
    "DEFAULT_OAUTH_SCOPES",
    "MCP_RESOURCE",
    "ManualApiToken",
    "NotFoundError",
    "OAuth2Client",
    "OAuthAuthorizationRequest",
    "PUBLIC_API_RESOURCE",
    "RateLimitError",
    "RawFetch",
    "ServerDownError",
    "SnekSDK",
]
