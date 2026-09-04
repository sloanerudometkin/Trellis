import json
from collections.abc import Callable
from functools import wraps
from typing import Any

import jwt
from flask import current_app, g, request
from sqlalchemy import text

from trellis.extensions import db


class AuthenticationError(Exception):
    pass


def _bearer_token() -> str:
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthenticationError("A valid Bearer token is required.")
    return token


def _decode_supabase_token(token: str) -> dict[str, Any]:
    supabase_url = current_app.config.get("SUPABASE_URL", "").rstrip("/")
    if not supabase_url:
        raise RuntimeError("SUPABASE_URL is required for JWT validation.")

    jwks_client = jwt.PyJWKClient(f"{supabase_url}/auth/v1/.well-known/jwks.json")
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256", "ES256"],
        audience=current_app.config["SUPABASE_JWT_AUDIENCE"],
        issuer=f"{supabase_url}/auth/v1",
    )


def decode_access_token(token: str) -> dict[str, Any]:
    decoder: Callable[[str], dict[str, Any]] | None = current_app.config.get(
        "JWT_DECODER"
    )
    try:
        claims = decoder(token) if decoder else _decode_supabase_token(token)
    except (jwt.PyJWTError, ValueError) as error:
        raise AuthenticationError("The access token is invalid or expired.") from error

    if not claims.get("sub"):
        raise AuthenticationError("The access token is missing its user identifier.")
    return claims


def apply_postgres_rls_context(claims: dict[str, Any]) -> None:
    """Make Supabase auth.uid() resolve to this request's verified user."""

    if db.engine.dialect.name != "postgresql":
        return
    db.session.execute(
        text("SELECT set_config('request.jwt.claims', :claims, true)"),
        {"claims": json.dumps(claims)},
    )
    db.session.execute(text("SET LOCAL ROLE authenticated"))


def require_auth(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        g.auth_claims = decode_access_token(_bearer_token())
        apply_postgres_rls_context(g.auth_claims)
        return view(*args, **kwargs)

    return wrapped_view


def token_rate_limit_key() -> str:
    return request.headers.get("Authorization", request.remote_addr or "unknown")
