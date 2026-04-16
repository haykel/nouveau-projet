from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase, RequestFactory, override_settings
from rest_framework.exceptions import AuthenticationFailed
from app.authentication import KeycloakAuthentication, require_role, _extract_roles
from app.views import hello, health


KEYCLOAK_SETTINGS = {
    "KEYCLOAK_URL": "http://localhost:8180",
    "KEYCLOAK_REALM": "investissement",
    "KEYCLOAK_CLIENT_ID": "backend",
}


class HealthTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_health_returns_ok(self):
        request = self.factory.get("/health/")
        response = health(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "ok"})

    def test_health_no_auth_required(self):
        request = self.factory.get("/health/")
        response = health(request)
        self.assertEqual(response.status_code, 200)


class ExtractRolesTest(SimpleTestCase):
    def test_extract_roles_from_realm_access(self):
        token = {"realm_access": {"roles": ["user", "admin"]}}
        self.assertEqual(_extract_roles(token), ["user", "admin"])

    def test_extract_roles_empty_when_missing(self):
        self.assertEqual(_extract_roles({}), [])

    def test_extract_roles_empty_realm_access(self):
        token = {"realm_access": {}}
        self.assertEqual(_extract_roles(token), [])


@override_settings(**KEYCLOAK_SETTINGS)
class KeycloakAuthenticationTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.auth = KeycloakAuthentication()

    def test_no_auth_header_returns_none(self):
        request = self.factory.get("/api/hello/")
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    def test_non_bearer_header_returns_none(self):
        request = self.factory.get("/api/hello/", HTTP_AUTHORIZATION="Basic abc123")
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    @patch("app.authentication.get_keycloak_public_key")
    @patch("app.authentication.jwt.decode")
    def test_valid_token_returns_user_info(self, mock_decode, mock_get_key):
        mock_get_key.return_value = "fake-public-key"
        mock_decode.return_value = {
            "sub": "user-123",
            "preferred_username": "haykel",
            "email": "haykel@test.com",
            "realm_access": {"roles": ["user"]},
        }
        request = self.factory.get("/api/hello/", HTTP_AUTHORIZATION="Bearer fake-token")
        user_info, token = self.auth.authenticate(request)

        self.assertEqual(user_info["sub"], "user-123")
        self.assertEqual(user_info["preferred_username"], "haykel")
        self.assertEqual(user_info["roles"], ["user"])
        self.assertEqual(token, "fake-token")

    @patch("app.authentication.get_keycloak_public_key")
    @patch("app.authentication.jwt.decode")
    def test_expired_token_raises(self, mock_decode, mock_get_key):
        import jwt as pyjwt
        mock_get_key.return_value = "fake-public-key"
        mock_decode.side_effect = pyjwt.ExpiredSignatureError()
        request = self.factory.get("/api/hello/", HTTP_AUTHORIZATION="Bearer expired")

        with self.assertRaises(AuthenticationFailed) as ctx:
            self.auth.authenticate(request)
        self.assertIn("expired", str(ctx.exception.detail))

    @patch("app.authentication.get_keycloak_public_key")
    @patch("app.authentication.jwt.decode")
    def test_invalid_token_raises(self, mock_decode, mock_get_key):
        import jwt as pyjwt
        mock_get_key.return_value = "fake-public-key"
        mock_decode.side_effect = pyjwt.InvalidTokenError("bad token")
        request = self.factory.get("/api/hello/", HTTP_AUTHORIZATION="Bearer bad")

        with self.assertRaises(AuthenticationFailed) as ctx:
            self.auth.authenticate(request)
        self.assertIn("Invalid token", str(ctx.exception.detail))


class RequireRoleTest(SimpleTestCase):
    def test_user_with_correct_role_passes(self):
        @require_role("user")
        def view(request):
            return "ok"

        request = MagicMock()
        request.user = {"roles": ["user", "admin"], "preferred_username": "haykel"}
        self.assertEqual(view(request), "ok")

    def test_user_without_role_raises(self):
        from rest_framework.exceptions import PermissionDenied

        @require_role("admin")
        def view(request):
            return "ok"

        request = MagicMock()
        request.user = {"roles": ["user"], "preferred_username": "haykel"}
        with self.assertRaises(PermissionDenied):
            view(request)

    def test_no_user_raises(self):
        @require_role("user")
        def view(request):
            return "ok"

        request = MagicMock()
        request.user = None
        with self.assertRaises(AuthenticationFailed):
            view(request)
