import pytest
from pydantic import ValidationError

from conftest import load_json_fixture
from trellis.recommendation_schemas import RecommendationBatch


def test_structured_recommendation_fixture_is_valid() -> None:
    batch = RecommendationBatch.model_validate(load_json_fixture("llm_recommendations_success.json"))
    assert {item.category for item in batch.suggestions} == {"aeo", "seo_content", "sem"}
    assert all(item.status == "pending" and item.stage == "suggested" for item in batch.suggestions)
    assert all(item.rationale for item in batch.suggestions)


def test_schema_rejects_missing_rationale() -> None:
    payload = load_json_fixture("llm_recommendations_success.json")
    del payload["suggestions"][0]["rationale"]
    with pytest.raises(ValidationError):
        RecommendationBatch.model_validate(payload)


def test_schema_rejects_missing_channel_or_category_specific_fields() -> None:
    payload = load_json_fixture("llm_recommendations_success.json")
    payload["suggestions"] = payload["suggestions"][:2]
    with pytest.raises(ValidationError, match="AEO, SEO/content, and SEM"):
        RecommendationBatch.model_validate(payload)

    payload = load_json_fixture("llm_recommendations_success.json")
    del payload["suggestions"][2]["cost_tier"]
    with pytest.raises(ValidationError, match="SEM recommendations require"):
        RecommendationBatch.model_validate(payload)


def test_schema_forbids_unexpected_model_fields() -> None:
    payload = load_json_fixture("llm_recommendations_success.json")
    payload["suggestions"][0]["invented_field"] = "unsafe"
    with pytest.raises(ValidationError):
        RecommendationBatch.model_validate(payload)
