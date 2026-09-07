"""Organic-only Health Score calculation and immutable run snapshots."""

from __future__ import annotations

from dataclasses import dataclass

from trellis.extensions import db
from trellis.models import AnalysisRun, AnalysisStatus, OrganizerStage, ResolutionStatus, SuggestionCategory


AEO_WEIGHT = 0.35
TECHNICAL_WEIGHT = 0.35
CONTENT_WEIGHT = 0.30
SCORING_DISCLOSURE = "Organic snapshot: 35% AEO completion, 35% resolved technical findings, and 30% published SEO/content work. SEM is excluded."


@dataclass(frozen=True)
class HealthScoreBreakdown:
    aeo_completion_pct: float
    technical_resolution_pct: float
    content_coverage_pct: float
    score: int


def completion_percentage(completed: int, total: int) -> float:
    if total <= 0:
        return 100.0
    return max(0.0, min(100.0, completed / total * 100))


def aeo_completion(analysis: AnalysisRun) -> float:
    suggestions = [item for item in analysis.suggestions if item.category == SuggestionCategory.AEO]
    published = sum(item.organizer_item is not None and item.organizer_item.stage == OrganizerStage.PUBLISHED for item in suggestions)
    return completion_percentage(published, len(suggestions))


def technical_resolution(analysis: AnalysisRun) -> float:
    resolved = sum(item.resolution_status == ResolutionStatus.RESOLVED for item in analysis.technical_findings)
    return completion_percentage(resolved, len(analysis.technical_findings))


def content_coverage(analysis: AnalysisRun) -> float:
    suggestions = [item for item in analysis.suggestions if item.category == SuggestionCategory.SEO_CONTENT]
    published = sum(item.organizer_item is not None and item.organizer_item.stage == OrganizerStage.PUBLISHED for item in suggestions)
    return completion_percentage(published, len(suggestions))


def calculate_health_score(analysis: AnalysisRun) -> HealthScoreBreakdown:
    aeo = aeo_completion(analysis)
    technical = technical_resolution(analysis)
    content = content_coverage(analysis)
    weighted = aeo * AEO_WEIGHT + technical * TECHNICAL_WEIGHT + content * CONTENT_WEIGHT
    score = max(0, min(100, int(weighted + 0.5)))
    return HealthScoreBreakdown(aeo, technical, content, score)


def persist_health_score(analysis: AnalysisRun) -> int:
    """Store a run's score once; later workflow changes cannot rewrite history."""
    if analysis.health_score is None:
        analysis.health_score = calculate_health_score(analysis).score
        db.session.commit()
    return analysis.health_score


def completed_health_history(analysis: AnalysisRun) -> list[AnalysisRun]:
    return list(db.session.scalars(
        db.select(AnalysisRun)
        .where(
            AnalysisRun.website_id == analysis.website_id,
            AnalysisRun.status == AnalysisStatus.COMPLETED,
            AnalysisRun.health_score.is_not(None),
        )
        .order_by(AnalysisRun.id)
    ).all())


def previous_health_score(analysis: AnalysisRun) -> int | None:
    previous = db.session.scalar(
        db.select(AnalysisRun.health_score)
        .where(
            AnalysisRun.website_id == analysis.website_id,
            AnalysisRun.status == AnalysisStatus.COMPLETED,
            AnalysisRun.health_score.is_not(None),
            AnalysisRun.id < analysis.id,
        )
        .order_by(AnalysisRun.id.desc())
        .limit(1)
    )
    return previous
