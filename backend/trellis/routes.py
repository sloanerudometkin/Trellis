import socket
import uuid

from flask import Blueprint, current_app, g, jsonify, request

from trellis.auth import require_auth, token_rate_limit_key
from trellis.analysis_jobs import launch_analysis
from trellis.analysis_pipeline import create_analysis_run
from trellis.extensions import db, limiter
from trellis.models import (
    AcceptanceStatus,
    AnalysisRun,
    AnalysisStatus,
    DismissReason,
    OrganizerItem,
    OrganizerStage,
    OrganizerStageHistory,
    Suggestion,
    User,
    Website,
    utc_now,
)
from trellis.schemas import (
    AnalysisRunResponse,
    HealthResponse,
    OrganizerItemResponse,
    OrganizerStageRequest,
    SuggestionDecisionRequest,
    SuggestionResponse,
    WebsiteCreateRequest,
    WebsiteResponse,
)
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


def owned_suggestion(suggestion_id: int) -> Suggestion | None:
    return db.session.scalar(
        db.select(Suggestion)
        .join(AnalysisRun)
        .join(Website)
        .where(Suggestion.id == suggestion_id, Website.user_id == current_user_id())
    )


def owned_organizer_item(item_id: int) -> OrganizerItem | None:
    return db.session.scalar(
        db.select(OrganizerItem)
        .join(Website)
        .where(OrganizerItem.id == item_id, Website.user_id == current_user_id())
    )


def suggestion_response(suggestion: Suggestion) -> dict:
    payload = {
        "id": suggestion.id,
        "category": suggestion.category.value,
        "title": suggestion.title,
        "description": suggestion.description,
        "starter_outline": suggestion.starter_outline,
        "rationale": suggestion.rationale,
        "priority": suggestion.priority.value,
        "status": suggestion.acceptance_status.value,
        "dismiss_reason": suggestion.dismiss_reason.value if suggestion.dismiss_reason else None,
        "stage": suggestion.organizer_item.stage.value if suggestion.organizer_item else "suggested",
        "organizer_item_id": suggestion.organizer_item.id if suggestion.organizer_item else None,
        "affected_page_url": suggestion.affected_page_url,
        "target_keywords": [
            {"phrase": link.keyword.phrase, "recommended_usage_count": link.recommended_usage_count}
            for link in suggestion.keyword_links
        ],
    }
    return serialize(SuggestionResponse.model_validate(payload))


def organizer_item_response(item: OrganizerItem) -> dict:
    return serialize(OrganizerItemResponse.model_validate({
        "id": item.id,
        "website_id": item.website_id,
        "suggestion_id": item.suggestion_id,
        "item_type": item.item_type.value,
        "title": item.title,
        "stage": item.stage.value,
        "published_at": item.published_at,
    }))


def analysis_response(analysis: AnalysisRun) -> dict:
    suggestions = [suggestion_response(suggestion) for suggestion in analysis.suggestions]
    payload = {
        "id": analysis.id,
        "website_id": analysis.website_id,
        "status": analysis.status.value,
        "last_completed_stage": analysis.last_completed_stage,
        "pages_scanned_count": analysis.pages_scanned_count,
        "error_message": analysis.error_message,
        "started_at": analysis.started_at,
        "completed_at": analysis.completed_at,
        "keywords": analysis.keywords,
        "suggestions": suggestions,
    }
    return serialize(AnalysisRunResponse.model_validate(payload))


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
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, OPTIONS"
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


@api.patch("/suggestions/<int:suggestion_id>/decision")
@limiter.limit("30 per minute", key_func=token_rate_limit_key)
@require_auth
def decide_suggestion(suggestion_id: int):
    suggestion = owned_suggestion(suggestion_id)
    if suggestion is None:
        return jsonify(error="not_found", message="Suggestion not found."), 404
    payload = SuggestionDecisionRequest.model_validate(request.get_json(silent=False))
    if payload.status == "accepted":
        suggestion.acceptance_status = AcceptanceStatus.ACCEPTED
        suggestion.dismiss_reason = None
        if suggestion.organizer_item is None:
            item = OrganizerItem(
                website_id=suggestion.analysis_run.website_id,
                suggestion=suggestion,
                item_type=suggestion.category,
                title=suggestion.title,
                stage=OrganizerStage.BACKLOG,
            )
            item.stage_history.append(OrganizerStageHistory(to_stage=OrganizerStage.BACKLOG))
            db.session.add(item)
    else:
        suggestion.acceptance_status = AcceptanceStatus.DISMISSED
        suggestion.dismiss_reason = DismissReason(payload.dismiss_reason)
        if suggestion.organizer_item is not None:
            db.session.delete(suggestion.organizer_item)
    db.session.commit()
    return jsonify(data=suggestion_response(suggestion))


def set_organizer_stage(item: OrganizerItem, stage: OrganizerStage) -> None:
    previous = item.stage
    if previous == stage:
        return
    item.stage = stage
    item.published_at = utc_now() if stage == OrganizerStage.PUBLISHED else None
    item.stage_history.append(OrganizerStageHistory(from_stage=previous, to_stage=stage))


@api.patch("/suggestions/<int:suggestion_id>/stage")
@limiter.limit("30 per minute", key_func=token_rate_limit_key)
@require_auth
def update_suggestion_stage(suggestion_id: int):
    suggestion = owned_suggestion(suggestion_id)
    if suggestion is None:
        return jsonify(error="not_found", message="Suggestion not found."), 404
    if suggestion.organizer_item is None:
        return jsonify(error="conflict", message="Accept the suggestion before changing its stage."), 409
    payload = OrganizerStageRequest.model_validate(request.get_json(silent=False))
    set_organizer_stage(suggestion.organizer_item, OrganizerStage(payload.stage))
    db.session.commit()
    return jsonify(data=suggestion_response(suggestion))


@api.get("/websites/<int:website_id>/organizer-items")
@limiter.limit("60 per minute", key_func=token_rate_limit_key)
@require_auth
def list_organizer_items(website_id: int):
    if owned_website(website_id) is None:
        return jsonify(error="not_found", message="Website workspace not found."), 404
    items = db.session.scalars(
        db.select(OrganizerItem)
        .where(OrganizerItem.website_id == website_id)
        .order_by(OrganizerItem.id)
    ).all()
    return jsonify(data=[organizer_item_response(item) for item in items])


@api.patch("/organizer-items/<int:item_id>")
@limiter.limit("30 per minute", key_func=token_rate_limit_key)
@require_auth
def update_organizer_item(item_id: int):
    item = owned_organizer_item(item_id)
    if item is None:
        return jsonify(error="not_found", message="Organizer item not found."), 404
    payload = OrganizerStageRequest.model_validate(request.get_json(silent=False))
    set_organizer_stage(item, OrganizerStage(payload.stage))
    db.session.commit()
    return jsonify(data=organizer_item_response(item))
