from decimal import Decimal
from uuid import UUID

import pytest

from conftest import load_json_fixture
from trellis.extensions import db
from trellis.models import AnalysisRun, CostTier, Keyword, Suggestion, SuggestionCategory, User, Website
from trellis.recommendation_schemas import RecommendationBatch
from trellis.recommendations import persist_recommendations
from trellis.sem_strategy import (
    CAMPAIGN_BOUNDARY,
    COST_TIER_DISCLOSURE,
    apply_sem_strategy,
    cheaper_alternatives,
    has_commercial_intent,
    infer_cost_tier,
    negative_keywords,
    rank_sem_candidates,
    targeting_guidance,
)


def analysis_record(context="A local garden nonprofit serving nearby neighborhoods."):
    user = User(id=UUID("00000000-0000-4000-8000-000000000001"), name="Owner", email="owner@example.com")
    analysis = AnalysisRun(website=Website(user=user, url="https://example.com", business_name="Garden Network", business_context=context))
    for phrase, frequency, score in [
        ("community garden", 3, "0.1"),
        ("garden", 12, "0.9"), ("garden workshops", 8, "0.8"),
        ("best local garden workshops", 5, "0.7"), ("garden workshops near me", 4, "0.6"),
    ]:
        analysis.keywords.append(Keyword(phrase=phrase, frequency=frequency, tfidf_score=Decimal(score)))
    db.session.add(user)
    db.session.commit()
    return analysis


@pytest.mark.parametrize(("phrase", "tier"), [("garden", CostTier.HIGH), ("garden workshops", CostTier.MEDIUM), ("local garden workshops", CostTier.LOW)])
def test_cost_tier_word_count_boundaries(phrase, tier):
    assert infer_cost_tier(phrase) == tier


@pytest.mark.parametrize("phrase", ["buy plants", "best garden service", "garden pricing", "garden near me"])
def test_commercial_intent_modifiers(phrase):
    assert has_commercial_intent(phrase)


def test_ranking_prioritizes_long_tail_commercial_lower_cost_candidates(app):
    ranked = rank_sem_candidates(analysis_record().keywords)
    assert ranked[0].keyword.phrase == "best local garden workshops"
    assert ranked[0].cost_tier == CostTier.LOW
    assert ranked[0].commercial_intent is True


def test_higher_cost_terms_receive_two_to_four_lower_cost_alternatives():
    alternatives = cheaper_alternatives("garden workshops")
    assert 2 <= len(alternatives) <= 4
    assert all(infer_cost_tier(item) == CostTier.LOW for item in alternatives)
    assert cheaper_alternatives("best local garden workshops") == []


def test_targeting_includes_network_audience_and_local_radius():
    local = targeting_guidance("A local service for Wilmington neighborhoods")
    assert "Search network" in local and "interests" in local and "15 miles" in local


def test_negative_keywords_exclude_terms_that_match_the_business(app):
    analysis = analysis_record("Free local DIY garden education")
    assert negative_keywords(analysis.keywords, analysis.website.business_context) == ["jobs", "how to"]


def test_off_topic_terms_surfaced_by_analysis_lead_the_negative_list(app):
    analysis = analysis_record("A paid neighborhood gardening service")
    analysis.keywords.append(Keyword(phrase="garden jobs", frequency=2, tfidf_score=Decimal("0.2")))
    assert negative_keywords(analysis.keywords, analysis.website.business_context)[0] == "jobs"


def test_strategy_persists_ad_group_landing_targeting_negatives_and_linked_alternatives(app):
    analysis = analysis_record()
    # Make the selected candidate medium cost so linked cheaper alternatives are required.
    analysis.keywords = [item for item in analysis.keywords if item.phrase in {"community garden", "garden workshops"}]
    persist_recommendations(analysis, RecommendationBatch.model_validate(load_json_fixture("llm_recommendations_success.json")))
    sem = db.session.scalars(db.select(Suggestion).where(Suggestion.category == SuggestionCategory.SEM).order_by(Suggestion.id)).all()
    primary = next(item for item in sem if item.cheaper_alternative_to_id is None)
    alternatives = [item for item in sem if item.cheaper_alternative_to_id == primary.id]
    assert primary.cost_tier == CostTier.MEDIUM
    assert primary.ad_group_label and primary.ad_copy_angle
    assert primary.landing_page_match == "https://example.com/"
    assert "Search network" in primary.targeting_notes and "15 miles" in primary.targeting_notes
    assert primary.negative_keywords == ["free", "jobs", "DIY", "how to"]
    assert 2 <= len(alternatives) <= 4
    assert all(item.cost_tier == CostTier.LOW for item in alternatives)


def test_strategy_builds_two_to_four_tightly_themed_primary_ad_groups(app):
    analysis = analysis_record()
    persist_recommendations(analysis, RecommendationBatch.model_validate(load_json_fixture("llm_recommendations_success.json")))
    sem = [item for item in analysis.suggestions if item.category == SuggestionCategory.SEM]
    primary = [item for item in sem if item.cheaper_alternative_to_id is None]
    assert 2 <= len(primary) <= 4
    assert len({item.ad_group_label for item in primary}) == len(primary)
    assert all("Quality Score" in item.rationale and "CPC" in item.rationale for item in primary)


def test_every_cost_tier_contract_has_disclosure_and_no_real_bid_values(app):
    analysis = analysis_record()
    persist_recommendations(analysis, RecommendationBatch.model_validate(load_json_fixture("llm_recommendations_success.json")))
    sem = [item for item in analysis.suggestions if item.category == SuggestionCategory.SEM]
    assert COST_TIER_DISCLOSURE
    assert all(item.cost_tier and item.cpc_low is None and item.cpc_high is None and item.search_volume is None for item in sem)


def test_no_campaign_launch_or_spending_route_exists(app):
    dangerous = ("campaign", "launch", "spend", "bid")
    mutation_routes = [rule.rule.casefold() for rule in app.url_map.iter_rules() if {"POST", "PATCH", "PUT", "DELETE"} & rule.methods]
    assert not any(term in route for route in mutation_routes for term in dangerous)
    assert "cannot create, launch, manage, bid on, or spend money" in CAMPAIGN_BOUNDARY
