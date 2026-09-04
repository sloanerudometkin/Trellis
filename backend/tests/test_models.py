from decimal import Decimal
from uuid import UUID

from trellis.extensions import db
from trellis.models import (
    AnalysisRun,
    AnalysisStatus,
    Keyword,
    OrganizerItem,
    OrganizerStage,
    OrganizerStageHistory,
    Report,
    Suggestion,
    SuggestionCategory,
    SuggestionKeyword,
    SuggestionPriority,
    SuggestionTechnicalFinding,
    TechnicalFinding,
    FindingSeverity,
    User,
    Website,
)


EXPECTED_TABLES = {
    "users",
    "websites",
    "analysis_runs",
    "keywords",
    "suggestions",
    "suggestion_keywords",
    "technical_findings",
    "suggestion_technical_findings",
    "reports",
    "organizer_items",
    "organizer_stage_history",
}


def test_mvp_schema_has_only_approved_tables(app) -> None:
    assert set(db.metadata.tables) == EXPECTED_TABLES
    assert "page_snapshots" not in db.metadata.tables
    assert "stage" not in db.metadata.tables["suggestions"].columns


def test_complete_mvp_relationship_graph_can_be_saved(app) -> None:
    user = User(
        id=UUID("00000000-0000-4000-8000-000000000001"),
        name="Test User",
        email="test@example.com",
    )
    website = Website(user=user, url="https://example.com/", business_name="Example")
    analysis = AnalysisRun(website=website, status=AnalysisStatus.COMPLETED, health_score=80)
    keyword = Keyword(analysis_run=analysis, phrase="community garden", frequency=4, tfidf_score=Decimal("0.75"))
    suggestion = Suggestion(
        analysis_run=analysis,
        category=SuggestionCategory.SEO_CONTENT,
        title="Create a planting guide",
        description="Add a practical guide.",
        rationale="Visitors need a clear starting point.",
        priority=SuggestionPriority.HIGH,
        affected_page_url="https://example.com/",
    )
    finding = TechnicalFinding(
        analysis_run=analysis,
        finding_type="missing_meta_description",
        severity=FindingSeverity.MEDIUM,
        explanation="The page needs a description.",
        affected_page_url="https://example.com/",
    )
    suggestion.keyword_links.append(SuggestionKeyword(keyword=keyword, recommended_usage_count=2))
    suggestion.technical_finding_links.append(SuggestionTechnicalFinding(technical_finding=finding))
    organizer_item = OrganizerItem(
        website=website,
        suggestion=suggestion,
        item_type=SuggestionCategory.SEO_CONTENT,
        title=suggestion.title,
        stage=OrganizerStage.BACKLOG,
    )
    organizer_item.stage_history.append(OrganizerStageHistory(to_stage=OrganizerStage.BACKLOG))
    report = Report(
        website=website,
        analysis_run=analysis,
        health_score=80,
        aeo_completion_pct=Decimal("25.00"),
        summary_text="The first test report.",
    )
    db.session.add(user)
    db.session.commit()

    assert website.analysis_runs == [analysis]
    assert analysis.report is report
    assert suggestion.organizer_item is organizer_item
    assert suggestion.keyword_links[0].keyword is keyword
    assert suggestion.technical_finding_links[0].technical_finding is finding
    assert organizer_item.stage_history[0].to_stage is OrganizerStage.BACKLOG
