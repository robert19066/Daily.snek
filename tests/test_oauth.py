import base64
import hashlib
import unittest
from urllib.parse import parse_qs, urlparse
from unittest.mock import Mock, patch

from snek.oauth import (
    AUTHORIZATION_ENDPOINT,
    MCP_RESOURCE,
    PUBLIC_API_RESOURCE,
    TOKEN_ENDPOINT,
    OAuth2Client,
)


class OAuthClientTests(unittest.TestCase):
    def test_authorization_request_uses_pkce_and_correct_resource(self):
        client = OAuth2Client("client-id", "client-secret")
        request = client.create_authorization_request("https://example.test/callback")
        query = parse_qs(urlparse(request.authorization_url).query)

        self.assertEqual(urlparse(request.authorization_url).scheme, "https")
        self.assertTrue(
            request.authorization_url.startswith(f"{AUTHORIZATION_ENDPOINT}?")
        )
        self.assertEqual(query["client_id"], ["client-id"])
        self.assertEqual(query["resource"], [PUBLIC_API_RESOURCE])
        self.assertEqual(query["code_challenge_method"], ["S256"])
        self.assertEqual(query["state"], [request.state])
        expected_challenge = (
            base64.urlsafe_b64encode(
                hashlib.sha256(request.code_verifier.encode("ascii")).digest()
            )
            .rstrip(b"=")
            .decode("ascii")
        )
        self.assertEqual(query["code_challenge"], [expected_challenge])

    def test_mcp_resource_is_explicitly_supported(self):
        client = OAuth2Client(
            "client-id",
            "client-secret",
            resource=MCP_RESOURCE,
        )
        request = client.create_authorization_request("https://example.test/callback")
        query = parse_qs(urlparse(request.authorization_url).query)

        self.assertEqual(query["resource"], [MCP_RESOURCE])

    def test_code_exchange_sends_verifier_secret_and_resource(self):
        response = Mock(content=b'{"access_token":"access"}')
        response.json.return_value = {"access_token": "access"}

        with patch("snek.oauth.requests.post", return_value=response) as post:
            client = OAuth2Client("client-id", "client-secret")
            tokens = client.exchange_code(
                "authorization-code",
                "https://example.test/callback",
                "pkce-verifier",
            )

        self.assertEqual(tokens, {"access_token": "access"})
        post.assert_called_once_with(
            TOKEN_ENDPOINT,
            data={
                "grant_type": "authorization_code",
                "code": "authorization-code",
                "redirect_uri": "https://example.test/callback",
                "client_id": "client-id",
                "client_secret": "client-secret",
                "code_verifier": "pkce-verifier",
                "resource": PUBLIC_API_RESOURCE,
            },
        )
        response.raise_for_status.assert_called_once()

    def test_refresh_and_revoke_use_oauth_endpoints(self):
        response = Mock(content=b'{"refresh_token":"rotated"}')
        response.json.return_value = {"refresh_token": "rotated"}
        empty_response = Mock(content=b"")

        with patch(
            "snek.oauth.requests.post", side_effect=[response, empty_response]
        ) as post:
            client = OAuth2Client("client-id", "client-secret")
            refreshed = client.refresh_access_token("refresh-token")
            revoked = client.revoke_token("rotated")

        self.assertEqual(refreshed, {"refresh_token": "rotated"})
        self.assertIsNone(revoked)
        self.assertEqual(post.call_args_list[0].args[0], TOKEN_ENDPOINT)
        self.assertEqual(
            post.call_args_list[0].kwargs["data"],
            {
                "grant_type": "refresh_token",
                "refresh_token": "refresh-token",
                "client_id": "client-id",
                "client_secret": "client-secret",
                "resource": PUBLIC_API_RESOURCE,
            },
        )
        self.assertEqual(
            post.call_args_list[1].kwargs["data"]["token"],
            "rotated",
        )
        response.raise_for_status.assert_called_once()
        empty_response.raise_for_status.assert_called_once()

    def test_empty_client_credentials_are_rejected(self):
        with self.assertRaises(ValueError):
            OAuth2Client("", "client-secret")
        with self.assertRaises(ValueError):
            OAuth2Client("client-id", "")


if __name__ == "__main__":
    unittest.main()
