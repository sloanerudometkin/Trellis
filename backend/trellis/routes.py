import uuid

from flask import Blueprint, current_app, g, jsonify, request

from trellis.auth import require_auth, token_rate_limit_key
from trellis.extensions import db, limiter
from trellis.models import User, Website
from trellis.schemas import HealthResponse, WebsiteCreateRequest, WebsiteResponse


api = Blueprint("api", __name__)


def serialize(model) -> dict:
    return model.model_dump(mode="json")


def current_user_id() -> uuid.UUID:
    try:
        return uuid.UUID(g.auth_claims["sub"])
    except (ValueError, TypeError) as error:
        from trellis.auth import AuthenticationError

        raise AuthenticationError("The access token has an invalid user identifier.") from error


def ensure_current_user() -> User:
    user_id = current_user_id()
    user = db.session.get(User, user_id)
    if user is None:
        email = g.auth_claims.get("email")
        if not email:
            from trellis.auth import AuthenticationError

            raise AuthenticationError("The access token is missing the user's email.")
        user = User(
            id=user_id,
            email=email,
            name=g.auth_claims.get("user_metadata", {}).get("name", email.split("@")[0]),
        )
        db.session.add(user)
        db.session.flush()
    return user


@api.after_request
def add_response_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    origin = current_app.config.get("FRONTEND_ORIGIN")
    if origin and request.headers.get("Origin") == origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Vary"] = "Origin"
    return response


@api.get("/health")
@limiter.limit("60 per minute")
def health():
    return jsonify(serialize(HealthResponse(status="ok", service="trellis-api")))


@api.get("/websites")
@limiter.limit("20 per minute", key_func=token_rate_limit_key)
@require_auth
def list_websites():
    websites = db.session.scalars(
        db.select(Website)
        .where(Website.user_id == current_user_id())
        .order_by(Website.id)
    ).all()
    return jsonify(
        data=[serialize(WebsiteResponse.model_validate(website)) for website in websites]
    )


@api.post("/websites")
@limiter.limit("10 per minute", key_func=token_rate_limit_key)
@require_auth
def create_website():
    payload = WebsiteCreateRequest.model_validate(request.get_json(silent=False))
    user = ensure_current_user()
    website = Website(
        user_id=user.id,
        url=str(payload.url),
        business_name=payload.business_name,
        business_context=payload.business_context,
    )
    db.session.add(website)
    db.session.commit()
    return jsonify(data=serialize(WebsiteResponse.model_validate(website))), 201
