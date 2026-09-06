import socket
import uuid

from flask import Blueprint, current_app, g, jsonify, request

from trellis.auth import require_auth, token_rate_limit_key
from trellis.analysis_jobs import launch_analysis
from trellis.analysis_pipeline import create_analysis_run
from trellis.extensions import db, limiter
from trellis.models import AnalysisRun, AnalysisStatus, User, Website
from trellis.schemas import AnalysisRunResponse, HealthResponse, WebsiteCreateRequest, WebsiteResponse
from trellis.url_safety import validate_public_url


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


def owned_website(website_id: int) -> Website | None:
    return db.session.scalar(db.select(Website).where(Website.id == website_id, Website.user_id == current_user_id()))


def owned_analysis(analysis_id: int) -> AnalysisRun | None:
    return db.session.scalar(
        db.select(AnalysisRun).join(Website).where(AnalysisRun.id == analysis_id, Website.user_id == current_user_id())
    )


def analysis_response(analysis: AnalysisRun) -> dict:
    return serialize(AnalysisRunResponse.model_validate(analysis))


def start_analysis_job(analysis_id: int) -> None:
    app = current_app._get_current_object()
    launcher = app.config.get("ANALYSIS_JOB_LAUNCHER") or launch_analysis
    launcher(app, analysis_id)


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
    normalized_url = validate_public_url(
        payload.url,
        resolver=current_app.config.get("URL_RESOLVER") or socket.getaddrinfo,
    )
    website = Website(
        user_id=user.id,
        url=normalized_url,
        business_name=payload.business_name,
        business_context=payload.business_context,
    )
    db.session.add(website)
    db.session.commit()
    return jsonify(data=serialize(WebsiteResponse.model_validate(website))), 201


@api.get("/websites/<int:website_id>")
@limiter.limit("20 per minute", key_func=token_rate_limit_key)
@require_auth
def get_website(website_id: int):
    website = owned_website(website_id)
    if website is None:
        return jsonify(error="not_found", message="Website workspace not found."), 404
    return jsonify(data=serialize(WebsiteResponse.model_validate(website)))


@api.post("/websites/<int:website_id>/analysis-runs")
@limiter.limit("5 per minute", key_func=token_rate_limit_key)
@require_auth
def create_website_analysis(website_id: int):
    website = owned_website(website_id)
    if website is None:
        return jsonify(error="not_found", message="Website workspace not found."), 404
    active = db.session.scalar(
        db.select(AnalysisRun).where(
            AnalysisRun.website_id == website.id,
            AnalysisRun.status.in_([
                AnalysisStatus.QUEUED,
                AnalysisStatus.SCRAPING,
                AnalysisStatus.ANALYZING,
                AnalysisStatus.GENERATING,
            ]),
        ).order_by(AnalysisRun.id.desc())
    )
    analysis = active or create_analysis_run(website)
    if active is None:
        start_analysis_job(analysis.id)
    return jsonify(data=analysis_response(analysis)), 202


@api.get("/analysis-runs/<int:analysis_id>")
@limiter.limit("60 per minute", key_func=token_rate_limit_key)
@require_auth
def get_analysis(analysis_id: int):
    analysis = owned_analysis(analysis_id)
    if analysis is None:
        return jsonify(error="not_found", message="Analysis run not found."), 404
    return jsonify(data=analysis_response(analysis))


@api.post("/analysis-runs/<int:analysis_id>/retry")
@limiter.limit("5 per minute", key_func=token_rate_limit_key)
@require_auth
def retry_analysis(analysis_id: int):
    analysis = owned_analysis(analysis_id)
    if analysis is None:
        return jsonify(error="not_found", message="Analysis run not found."), 404
    if analysis.status == AnalysisStatus.COMPLETED:
        return jsonify(data=analysis_response(analysis)), 200
    if analysis.status != AnalysisStatus.FAILED:
        return jsonify(error="conflict", message="Only a failed analysis can be retried."), 409
    analysis.status = AnalysisStatus.QUEUED
    analysis.error_message = None
    analysis.completed_at = None
    db.session.commit()
    start_analysis_job(analysis.id)
    return jsonify(data=analysis_response(analysis)), 202
