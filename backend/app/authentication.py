import jwt
import requests
from functools import wraps
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


def get_keycloak_public_key():
    """Fetch the realm's public key from Keycloak."""
    url = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        key = response.json()["public_key"]
        return f"-----BEGIN PUBLIC KEY-----\n{key}\n-----END PUBLIC KEY-----"
    except requests.RequestException as e:
        raise AuthenticationFailed(f"Cannot reach Keycloak: {e}")


class KeycloakAuthentication(BaseAuthentication):
    """Authenticate requests using a Keycloak JWT Bearer token."""

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split("Bearer ")[1]
        try:
            public_key = get_keycloak_public_key()
            decoded = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                options={"verify_exp": True, "verify_aud": False},
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f"Invalid token: {e}")

        user_info = {
            "sub": decoded.get("sub"),
            "preferred_username": decoded.get("preferred_username"),
            "email": decoded.get("email"),
            "roles": _extract_roles(decoded),
        }
        return (user_info, token)


def _extract_roles(decoded_token):
    """Extract realm roles from the decoded JWT."""
    realm_access = decoded_token.get("realm_access", {})
    return realm_access.get("roles", [])


def require_role(role):
    """Decorator that requires a specific Keycloak realm role."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user or not isinstance(request.user, dict):
                raise AuthenticationFailed("Authentication required")
            user_roles = request.user.get("roles", [])
            if role not in user_roles:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(f"Role '{role}' is required")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
