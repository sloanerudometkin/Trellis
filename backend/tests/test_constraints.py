from decimal import Decimal
from uuid import UUID

import pytest
from sqlalchemy.exc import IntegrityError, StatementError

from trellis.extensions import db
from trellis.models import (
    AcceptanceStatus,
    AnalysisRun,
    Report,
    Suggestion,
    SuggestionCategory,
    SuggestionPriority,
    User,
    Website,
)


def add_user_and_website() -> tuple[User, Website]:
    user = User(
        id=UUID("00000000-0000-4000-8000-000000000001"),
        name="Test User",
        email="test@example.com",
    )
    website = Website(user=user, url="https://example.com/", business_name="Example")
    db.session.add(user)
    db.session.flush()
    return user, website


def assert_commit_fails(error_type=IntegrityError) -> None:
    with pytest.raises(error_type):
        db.session.commit()
    db.session.rollback()


def test_required_field_rejects_null(app) -> None:
    db.session.add(User(id=UUID("00000000-0000-4000-8000-000000000001"), name=None, email="test@example.com"))
    assert_commit_fails()


def test_email_and_per_user_website_are_unique(app) -> None:
    user, website = add_user_and_website()
    db.session.commit()
    db.session.add(Website(user=user, url=website.url, business_name="Duplicate"))
    assert_commit_fails()


def test_foreign_key_rejects_missing_parent(app) -> None:
    db.session.add(Website(user_id=UUID("00000000-0000-4000-8000-000000000099"), url="https://example.com/", business_name="Orphan"))
    assert_commit_fails()


def test_health_score_must_be_between_zero_and_one_hundred(app) -> None:
    _, website = add_user_and_website()
    db.session.add(AnalysisRun(website=website, health_score=101))
    assert_commit_fails()


def test_invalid_enum_value_is_rejected(app) -> None:
    _, website = add_user_and_website()
    db.session.add(AnalysisRun(website=website, status="not-a-status"))
    assert_commit_fails(StatementError)


def test_dismissed_suggestion_requires_reason(app) -> None:
    _, website = add_user_and_website()
    analysis = AnalysisRun(website=website)
    db.session.add(
        Suggestion(
            analysis_run=analysis,
            category=SuggestionCategory.AEO,
            title="Add an answer",
            description="Add a direct answer.",
            rationale="It helps answer engines.",
            priority=SuggestionPriority.HIGH,
            acceptance_status=AcceptanceStatus.DISMISSED,
        )
    )
    assert_commit_fails()


def test_non_sem_suggestion_rejects_sem_fields(app) -> None:
    _, website = add_user_and_website()
    analysis = AnalysisRun(website=website)
    db.session.add(
        Suggestion(
            analysis_run=analysis,
            category=SuggestionCategory.AEO,
            title="Add an answer",
            description="Add a direct answer.",
            rationale="It helps answer engines.",
            priority=SuggestionPriority.HIGH,
            cost_tier="low",
        )
    )
    assert_commit_fails()


def test_analysis_run_can_have_only_one_report(app) -> None:
    _, website = add_user_and_website()
    analysis = AnalysisRun(website=website)
    first_report = Report(
        website=website,
        analysis_run=analysis,
        health_score=50,
        aeo_completion_pct=Decimal("10.00"),
        summary_text="First",
    )
    db.session.add(first_report)
    db.session.commit()
    db.session.add(
        Report(
            website_id=website.id,
            analysis_run_id=analysis.id,
            health_score=50,
            aeo_completion_pct=Decimal("10.00"),
            summary_text="Duplicate",
        )
    )
    assert_commit_fails()
