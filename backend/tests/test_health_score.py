from uuid import UUID

import pytest

from trellis.extensions import db
from trellis.health_score import (
    AEO_WEIGHT,
    CONTENT_WEIGHT,
    TECHNICAL_WEIGHT,
    aeo_completion,
    calculate_health_score,
    completion_percentage,
    content_coverage,
    persist_health_score,
    previous_health_score,
    technical_resolution,
)
from trellis.routes import analysis_response
from trellis.models import (
    AnalysisRun, AnalysisStatus, FindingSeverity, OrganizerItem, OrganizerStage,
    ResolutionStatus, Suggestion, SuggestionCategory, SuggestionPriority,
    TechnicalFinding, User, Website,
)


def suggestion(category, title, published=False):
    item = Suggestion(category=category, title=title, description="A useful recommendation.", rationale="This matters for the analyzed website.", priority=SuggestionPriority.MEDIUM)
    if published:
        item.organizer_item = OrganizerItem(website_id=1, item_type=category, title=title, stage=OrganizerStage.PUBLISHED)
    return item


def analysis_record():
    user = User(id=UUID("00000000-0000-4000-8000-000000000001"), name="Owner", email="owner@example.com")
    website = Website(user=user, url="https://example.com", business_name="Example")
    analysis = AnalysisRun(website=website, status=AnalysisStatus.GENERATING)
    db.session.add(user)
    db.session.commit()
    return analysis


@pytest.mark.parametrize(("completed", "total", "expected"), [(0, 0, 100), (0, 4, 0), (2, 4, 50), (4, 4, 100), (8, 4, 100)])
def test_component_percentage_boundaries(completed, total, expected):
    assert completion_percentage(completed, total) == expected


def test_aeo_component_counts_only_published_aeo_items(app):
    analysis = analysis_record()
    analysis.suggestions.extend([suggestion(SuggestionCategory.AEO, "AEO one", True), suggestion(SuggestionCategory.AEO, "AEO two"), suggestion(SuggestionCategory.SEM, "Paid", True)])
    assert aeo_completion(analysis) == 50


def test_technical_component_counts_only_resolved_findings(app):
    analysis = analysis_record()
    analysis.technical_findings.extend([
        TechnicalFinding(finding_type="title", severity=FindingSeverity.HIGH, explanation="Fix title", resolution_status=ResolutionStatus.RESOLVED),
        TechnicalFinding(finding_type="h1", severity=FindingSeverity.MEDIUM, explanation="Fix heading"),
    ])
    assert technical_resolution(analysis) == 50


def test_content_component_counts_only_published_seo_content(app):
    analysis = analysis_record()
    analysis.suggestions.extend([suggestion(SuggestionCategory.SEO_CONTENT, "Guide one", True), suggestion(SuggestionCategory.SEO_CONTENT, "Guide two"), suggestion(SuggestionCategory.SEM, "Paid", True)])
    assert content_coverage(analysis) == 50


def test_documented_weighting_and_rounding(app):
    assert AEO_WEIGHT + TECHNICAL_WEIGHT + CONTENT_WEIGHT == 1
    analysis = analysis_record()
    analysis.suggestions.extend([suggestion(SuggestionCategory.AEO, "AEO", True), suggestion(SuggestionCategory.SEO_CONTENT, "Content")])
    analysis.technical_findings.extend([
        TechnicalFinding(finding_type="one", severity=FindingSeverity.HIGH, explanation="One", resolution_status=ResolutionStatus.RESOLVED),
        TechnicalFinding(finding_type="two", severity=FindingSeverity.MEDIUM, explanation="Two"),
    ])
    breakdown = calculate_health_score(analysis)
    assert (breakdown.aeo_completion_pct, breakdown.technical_resolution_pct, breakdown.content_coverage_pct) == (100, 50, 0)
    assert breakdown.score == 53


def test_scores_are_always_bounded(app):
    analysis = analysis_record()
    assert calculate_health_score(analysis).score == 100
    analysis.suggestions.extend([suggestion(SuggestionCategory.AEO, "AEO"), suggestion(SuggestionCategory.SEO_CONTENT, "Content")])
    analysis.technical_findings.append(TechnicalFinding(finding_type="open", severity=FindingSeverity.HIGH, explanation="Open"))
    assert calculate_health_score(analysis).score == 0


def test_sem_data_never_changes_the_organic_score(app):
    analysis = analysis_record()
    baseline = calculate_health_score(analysis)
    analysis.suggestions.extend([suggestion(SuggestionCategory.SEM, "High paid", True), suggestion(SuggestionCategory.SEM, "Low paid")])
    assert calculate_health_score(analysis) == baseline


def test_each_analysis_keeps_one_immutable_score_snapshot(app):
    first = analysis_record()
    first.suggestions.append(suggestion(SuggestionCategory.AEO, "AEO"))
    original = persist_health_score(first)
    first.suggestions[0].organizer_item = OrganizerItem(item_type=SuggestionCategory.AEO, title="AEO", stage=OrganizerStage.PUBLISHED)
    assert persist_health_score(first) == original == 65


def test_first_run_has_no_delta_and_later_run_uses_prior_snapshot(app):
    first = analysis_record()
    first.health_score = 42
    first.status = AnalysisStatus.COMPLETED
    db.session.commit()
    assert previous_health_score(first) is None
    second = AnalysisRun(website=first.website, status=AnalysisStatus.COMPLETED, health_score=70)
    db.session.add(second)
    db.session.commit()
    assert previous_health_score(second) == 42
    assert second.health_score - previous_health_score(second) == 28


def test_analysis_api_serializes_first_run_and_later_delta_history(app):
    first = analysis_record()
    first.health_score = 42
    first.status = AnalysisStatus.COMPLETED
    second = AnalysisRun(website=first.website, status=AnalysisStatus.COMPLETED, health_score=70)
    db.session.add(second)
    db.session.commit()

    first_payload = analysis_response(first)
    second_payload = analysis_response(second)
    assert first_payload["health_score_delta"] is None
    assert second_payload["health_score_delta"] == 28
    assert [point["score"] for point in second_payload["health_score_history"]] == [42, 70]
    assert "SEM is excluded" in second_payload["health_score_disclosure"]
