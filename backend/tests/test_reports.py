from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from trellis.extensions import db
from trellis.models import (
    AcceptanceStatus, AnalysisRun, AnalysisStatus, CostTier, FindingSeverity,
    Keyword, OrganizerItem, OrganizerStage, Report, ResolutionStatus, Suggestion,
    SuggestionCategory, SuggestionPriority, TechnicalFinding, User, Website,
)
from trellis.reports import SNAPSHOT_DISCLOSURE, compare_reports, create_report_snapshot


def setup_report_data() -> tuple[Website, AnalysisRun]:
    user = User(id=UUID("00000000-0000-4000-8000-000000000001"), name="Owner", email="owner@example.com")
    website = Website(user=user, url="https://example.com", business_name="Example")
    run = AnalysisRun(website=website, status=AnalysisStatus.COMPLETED, health_score=72, completed_at=datetime(2026, 9, 7, tzinfo=timezone.utc))
    run.keywords.extend([
        Keyword(phrase="second", frequency=3, tfidf_score=Decimal("0.9")),
        Keyword(phrase="first", frequency=5, tfidf_score=Decimal("0.8")),
    ])
    aeo = Suggestion(analysis_run=run, category=SuggestionCategory.AEO, title="Answer", description="Answer it", rationale="Useful", priority=SuggestionPriority.HIGH, acceptance_status=AcceptanceStatus.ACCEPTED)
    sem = Suggestion(analysis_run=run, category=SuggestionCategory.SEM, title="Ad", description="Plan it", rationale="Useful", priority=SuggestionPriority.MEDIUM, acceptance_status=AcceptanceStatus.ACCEPTED, cost_tier=CostTier.LOW, ad_group_label="Core")
    run.technical_findings.extend([
        TechnicalFinding(finding_type="one", severity=FindingSeverity.HIGH, explanation="Open", resolution_status=ResolutionStatus.OPEN),
        TechnicalFinding(finding_type="two", severity=FindingSeverity.LOW, explanation="Done", resolution_status=ResolutionStatus.RESOLVED),
    ])
    website.organizer_items.extend([
        OrganizerItem(suggestion=aeo, item_type=SuggestionCategory.AEO, title="Answer", stage=OrganizerStage.PUBLISHED, published_at=datetime(2026, 9, 6, tzinfo=timezone.utc)),
        OrganizerItem(suggestion=sem, item_type=SuggestionCategory.SEM, title="Ad", stage=OrganizerStage.BACKLOG),
    ])
    db.session.add(user); db.session.commit()
    return website, run


def test_every_predefined_kpi_is_snapshotted_and_generation_is_idempotent(app) -> None:
    website, run = setup_report_data()
    report = create_report_snapshot(run); same = create_report_snapshot(run); db.session.commit()
    assert report.id == same.id
    assert db.session.scalar(db.select(db.func.count(Report.id))) == 1
    assert report.health_score == 72 and report.health_score_delta is None
    assert report.aeo_completion_pct == Decimal("100.00") and report.aeo_completion_delta is None
    assert (report.technical_findings_resolved, report.technical_findings_open) == (1, 1)
    assert report.content_published_count == 1 and report.top_keywords == ["first", "second"]
    assert report.sem_accepted_count == 1 and report.sem_cost_tier_breakdown == {"low": 1, "medium": 0, "high": 0}
    assert report.ad_groups_defined_count == 1
    assert report.organizer_stage_counts == {"backlog": 1, "in_production": 0, "in_review": 0, "published": 1}
    assert "First KPI snapshot" in report.summary_text


def test_old_snapshot_does_not_change_when_source_data_or_formula_changes(app) -> None:
    website, first_run = setup_report_data()
    first = create_report_snapshot(first_run); db.session.commit()
    original = (first.health_score, first.aeo_completion_pct, list(first.top_keywords), dict(first.organizer_stage_counts))
    first_run.health_score = 5
    website.organizer_items[0].stage = OrganizerStage.BACKLOG
    second_run = AnalysisRun(website=website, status=AnalysisStatus.COMPLETED, health_score=80, completed_at=datetime(2026, 10, 7, tzinfo=timezone.utc))
    second_run.keywords.append(Keyword(phrase="new", frequency=1, tfidf_score=Decimal("1")))
    db.session.add(second_run); db.session.flush(); create_report_snapshot(second_run); db.session.commit(); db.session.refresh(first)
    assert (first.health_score, first.aeo_completion_pct, first.top_keywords, first.organizer_stage_counts) == original


def report_with(website: Website, score: int, *, aeo: str, keyword: str) -> Report:
    run = AnalysisRun(website=website, status=AnalysisStatus.COMPLETED, health_score=score)
    report = Report(website=website, analysis_run=run, health_score=score, aeo_completion_pct=Decimal(aeo), technical_findings_resolved=0, technical_findings_open=0, content_published_count=0, top_keywords=[keyword] if keyword else [], sem_accepted_count=0, sem_cost_tier_breakdown={}, ad_groups_defined_count=0, organizer_stage_counts={}, summary_text="Snapshot")
    db.session.add(report); db.session.flush(); return report


def test_comparison_calculates_absolute_percentage_zero_and_keyword_empty_cases(app) -> None:
    website, _ = setup_report_data()
    before = report_with(website, 50, aeo="0", keyword="old")
    after = report_with(website, 75, aeo="20", keyword="")
    result = compare_reports(before, after)
    assert result["health_score"] == {"absolute": 25.0, "percentage": 50.0}
    assert result["aeo_completion_pct"] == {"absolute": 20.0, "percentage": None}
    assert result["sem_cost_tier_low"] == {"absolute": 0.0, "percentage": None}
    assert result["top_keywords"] == {"added": [], "removed": ["old"]}


def test_report_history_reopen_compare_and_user_isolation(client, app, user_one_headers, user_two_headers) -> None:
    with app.app_context():
        website, _ = setup_report_data(); before = report_with(website, 50, aeo="0", keyword="old"); after = report_with(website, 75, aeo="20", keyword="new"); db.session.commit()
        website_id, before_id, after_id = website.id, before.id, after.id
    history = client.get(f"/api/v1/websites/{website_id}/reports", headers=user_one_headers)
    assert history.status_code == 200 and len(history.get_json()["data"]) == 2
    reopened = client.get(f"/api/v1/reports/{before_id}", headers=user_one_headers)
    assert reopened.status_code == 200 and reopened.get_json()["data"]["disclosure"] == SNAPSHOT_DISCLOSURE
    compared = client.get(f"/api/v1/websites/{website_id}/report-comparison?before={before_id}&after={after_id}", headers=user_one_headers)
    assert compared.status_code == 200 and compared.get_json()["data"]["deltas"]["health_score"]["absolute"] == 25
    assert client.get(f"/api/v1/reports/{before_id}", headers=user_two_headers).status_code == 404
