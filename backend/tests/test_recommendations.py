import json
from decimal import Decimal
from uuid import UUID

import httpx
import pytest

from conftest import load_json_fixture
from trellis.extensions import db
from trellis.analysis_pipeline import execute_analysis_run
from trellis.models import AcceptanceStatus, AnalysisRun, AnalysisStatus, Keyword, Suggestion, User, Website
from trellis.recommendation_schemas import RecommendationBatch
from trellis.recommendations import (
    RecommendationProviderError,
    build_recommendation_prompt,
    generate_recommendations,
    persist_recommendations,
)


SUCCESS = load_json_fixture("llm_recommendations_success.json")


def analysis_record(context: str = "Contact Pat at pat@example.com or 302-555-0199.") -> AnalysisRun:
    user = User(id=UUID("00000000-0000-4000-8000-000000000001"), name="Owner", email="owner@example.com")
    website = Website(user=user, url="https://example.com", business_name="Garden Network", business_context=context)
    analysis = AnalysisRun(website=website, pages_scanned_count=3)
    analysis.keywords.append(Keyword(phrase="community garden", frequency=5, tfidf_score=Decimal("0.8")))
    db.session.add(user)
    db.session.commit()
    return analysis


def groq_response(request: httpx.Request, content: str, status: int = 200) -> httpx.Response:
    body = {"choices": [{"message": {"content": content}}]} if status == 200 else load_json_fixture("llm_outage_error.json")
    return httpx.Response(status, json=body, request=request)


def gemini_response(request: httpx.Request, content: str) -> httpx.Response:
    return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": content}]}}]}, request=request)


def test_prompt_contains_site_context_keywords_and_removes_pii(app) -> None:
    prompt = build_recommendation_prompt(analysis_record())
    assert "https://example.com" in prompt
    assert "Garden Network" in prompt
    assert "community garden" in prompt
    assert "pat@example.com" not in prompt and "302-555-0199" not in prompt
    assert "[redacted email]" in prompt and "[redacted phone]" in prompt
    assert "exactly from the ranked site keywords" in prompt
    assert "Required JSON schema" in prompt


def test_groq_success_uses_one_structured_output_call() -> None:
    requests: list[httpx.Request] = []
    def handler(request: httpx.Request):
        requests.append(request)
        return groq_response(request, json.dumps(SUCCESS))
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        batch = generate_recommendations("site prompt", client=client, groq_api_key="groq-test", gemini_api_key="")
    assert len(batch.suggestions) == 3
    assert len(requests) == 1
    sent = json.loads(requests[0].content)
    assert sent["response_format"] == {"type": "json_object"}
    assert requests[0].headers["authorization"] == "Bearer groq-test"


def test_malformed_groq_output_gets_exactly_one_retry() -> None:
    calls = 0
    def handler(request: httpx.Request):
        nonlocal calls
        calls += 1
        content = "not json" if calls == 1 else json.dumps(SUCCESS)
        return groq_response(request, content)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        batch = generate_recommendations("site prompt", client=client, groq_api_key="key", gemini_api_key="")
    assert calls == 2
    assert len(batch.suggestions) == 3


def test_two_invalid_groq_responses_stop_after_one_retry() -> None:
    calls = 0
    def handler(request: httpx.Request):
        nonlocal calls
        calls += 1
        return groq_response(request, json.dumps(load_json_fixture("llm_malformed.json")))
    with httpx.Client(transport=httpx.MockTransport(handler)) as client, pytest.raises(RecommendationProviderError):
        generate_recommendations("site prompt", client=client, groq_api_key="key", gemini_api_key="")
    assert calls == 2


@pytest.mark.parametrize("groq_status", [429, 503])
def test_groq_rate_limit_or_outage_falls_back_to_gemini(groq_status: int) -> None:
    hosts: list[str] = []
    def handler(request: httpx.Request):
        hosts.append(request.url.host)
        if request.url.host == "api.groq.com":
            body = load_json_fixture("llm_rate_limit_error.json") if groq_status == 429 else load_json_fixture("llm_outage_error.json")
            return httpx.Response(groq_status, json=body, request=request)
        return gemini_response(request, json.dumps(SUCCESS))
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        batch = generate_recommendations("site prompt", client=client, groq_api_key="groq", gemini_api_key="gemini")
    assert len(batch.suggestions) == 3
    assert hosts == ["api.groq.com", "generativelanguage.googleapis.com"]


def test_invalid_groq_retry_then_gemini_fallback() -> None:
    hosts: list[str] = []
    def handler(request: httpx.Request):
        hosts.append(request.url.host)
        if request.url.host == "api.groq.com":
            return groq_response(request, "{bad json")
        return gemini_response(request, json.dumps(SUCCESS))
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        generate_recommendations("site prompt", client=client, groq_api_key="groq", gemini_api_key="gemini")
    assert hosts == ["api.groq.com", "api.groq.com", "generativelanguage.googleapis.com"]


def test_only_validated_recommendations_are_persisted_with_required_state(app) -> None:
    analysis = analysis_record("A neighborhood gardening nonprofit.")
    batch = RecommendationBatch.model_validate(SUCCESS)
    persist_recommendations(analysis, batch)
    saved = db.session.scalars(db.select(Suggestion).where(Suggestion.analysis_run_id == analysis.id)).all()
    assert len(saved) == 3
    assert all(item.rationale and item.priority and item.category for item in saved)
    assert all(item.acceptance_status == AcceptanceStatus.PENDING for item in saved)
    content = next(item for item in saved if item.category.value == "seo_content")
    assert [(link.keyword.phrase, link.recommended_usage_count) for link in content.keyword_links] == [("community garden", 4)]
    assert "stage" not in db.metadata.tables["suggestions"].columns


def test_invalid_output_cannot_reach_persistence(app) -> None:
    analysis = analysis_record()
    with pytest.raises(Exception):
        malformed = RecommendationBatch.model_validate(load_json_fixture("llm_malformed.json"))
        persist_recommendations(analysis, malformed)
    assert analysis.suggestions == []


def test_generating_pipeline_stage_persists_validated_suggestions(app) -> None:
    analysis = analysis_record("A neighborhood gardening nonprofit.")
    analysis.status = AnalysisStatus.FAILED
    analysis.last_completed_stage = AnalysisStatus.ANALYZING.value
    db.session.commit()

    completed = execute_analysis_run(
        analysis,
        recommendation_generator=lambda run: persist_recommendations(
            run, RecommendationBatch.model_validate(SUCCESS)
        ),
    )
    assert completed.status == AnalysisStatus.COMPLETED
    assert completed.last_completed_stage == AnalysisStatus.GENERATING.value
    assert len(completed.suggestions) == 3


def test_invalid_generation_marks_run_failed_without_saving_suggestions(app) -> None:
    analysis = analysis_record()
    analysis.status = AnalysisStatus.FAILED
    analysis.last_completed_stage = AnalysisStatus.ANALYZING.value
    db.session.commit()

    def invalid_generator(_run: AnalysisRun) -> None:
        RecommendationBatch.model_validate(load_json_fixture("llm_malformed.json"))

    failed = execute_analysis_run(analysis, recommendation_generator=invalid_generator)
    assert failed.status == AnalysisStatus.FAILED
    assert failed.last_completed_stage == AnalysisStatus.ANALYZING.value
    assert failed.suggestions == []
