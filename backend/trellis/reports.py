"""Create immutable KPI snapshots and compare two saved Trellis reports."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import func

from trellis.extensions import db
from trellis.models import (
    AcceptanceStatus,
    AnalysisRun,
    CostTier,
    OrganizerItem,
    OrganizerStage,
    Report,
    ResolutionStatus,
    Suggestion,
    SuggestionCategory,
    TechnicalFinding,
)


SNAPSHOT_DISCLOSURE = (
    "Saved snapshot: these KPI values will not change later, even if your work, website, "
    "or Trellis scoring formula changes. SEM values are heuristic planning indicators, not live ad results."
)


def _percent(part: int, whole: int) -> Decimal:
    return Decimal("0.00") if whole == 0 else (Decimal(part) * 100 / Decimal(whole)).quantize(Decimal("0.01"))


def _previous_report(analysis: AnalysisRun) -> Report | None:
    return db.session.scalar(
        db.select(Report)
        .where(Report.website_id == analysis.website_id, Report.analysis_run_id != analysis.id)
        .order_by(Report.generated_at.desc(), Report.id.desc())
    )


def create_report_snapshot(analysis: AnalysisRun) -> Report:
    """Create exactly one report for a completed analysis; repeated calls are safe."""
    if analysis.report is not None:
        return analysis.report
    if analysis.health_score is None:
        raise ValueError("A completed analysis needs a Health Score before its Report can be generated.")

    previous = _previous_report(analysis)
    aeo_total = db.session.scalar(
        db.select(func.count(Suggestion.id)).join(AnalysisRun).where(
            AnalysisRun.website_id == analysis.website_id,
            AnalysisRun.id <= analysis.id,
            Suggestion.category == SuggestionCategory.AEO,
        )
    ) or 0
    aeo_completed = db.session.scalar(
        db.select(func.count(OrganizerItem.id))
        .join(Suggestion, OrganizerItem.suggestion_id == Suggestion.id)
        .where(
            OrganizerItem.website_id == analysis.website_id,
            OrganizerItem.stage == OrganizerStage.PUBLISHED,
            Suggestion.category == SuggestionCategory.AEO,
        )
    ) or 0
    aeo_pct = _percent(min(aeo_completed, aeo_total), aeo_total)

    resolved = sum(item.resolution_status == ResolutionStatus.RESOLVED for item in analysis.technical_findings)
    open_count = sum(item.resolution_status == ResolutionStatus.OPEN for item in analysis.technical_findings)
    period_start = previous.generated_at if previous else None
    published_query = db.select(func.count(OrganizerItem.id)).where(
        OrganizerItem.website_id == analysis.website_id,
        OrganizerItem.stage == OrganizerStage.PUBLISHED,
        OrganizerItem.published_at.is_not(None),
    )
    if period_start is not None:
        published_query = published_query.where(OrganizerItem.published_at > period_start)
    if analysis.completed_at is not None:
        published_query = published_query.where(OrganizerItem.published_at <= analysis.completed_at)
    published_count = db.session.scalar(published_query) or 0

    accepted_sem = db.session.scalars(
        db.select(Suggestion).join(AnalysisRun).where(
            AnalysisRun.website_id == analysis.website_id,
            AnalysisRun.id <= analysis.id,
            Suggestion.category == SuggestionCategory.SEM,
            Suggestion.acceptance_status == AcceptanceStatus.ACCEPTED,
        )
    ).all()
    tiers = {tier.value: sum(item.cost_tier == tier for item in accepted_sem) for tier in CostTier}
    stages = {
        stage.value: db.session.scalar(
            db.select(func.count(OrganizerItem.id)).where(
                OrganizerItem.website_id == analysis.website_id,
                OrganizerItem.stage == stage,
            )
        ) or 0
        for stage in OrganizerStage
    }
    top_keywords = [item.phrase for item in sorted(
        analysis.keywords,
        key=lambda item: (-item.frequency, -float(item.tfidf_score), item.phrase),
    )[:10]]
    health_delta = analysis.health_score - previous.health_score if previous else None
    aeo_delta = aeo_pct - previous.aeo_completion_pct if previous else None
    change_parts = [
        "First KPI snapshot saved" if previous is None else f"Health Score {('up' if health_delta >= 0 else 'down')} {abs(health_delta)} points",
        f"{published_count} card{'s' if published_count != 1 else ''} published",
        f"{len(top_keywords)} top keyword candidate{'s' if len(top_keywords) != 1 else ''} captured",
    ]
    report = Report(
        website_id=analysis.website_id,
        analysis_run=analysis,
        generated_at=analysis.completed_at,
        health_score=analysis.health_score,
        health_score_delta=health_delta,
        aeo_completion_pct=aeo_pct,
        aeo_completion_delta=aeo_delta,
        technical_findings_resolved=resolved,
        technical_findings_open=open_count,
        content_published_count=published_count,
        top_keywords=top_keywords,
        sem_accepted_count=len(accepted_sem),
        sem_cost_tier_breakdown=tiers,
        ad_groups_defined_count=sum(bool(item.ad_group_label) for item in analysis.suggestions if item.category == SuggestionCategory.SEM),
        organizer_stage_counts=stages,
        summary_text="; ".join(change_parts) + ".",
    )
    db.session.add(report)
    db.session.flush()
    return report


def _delta(before: int | float | Decimal | None, after: int | float | Decimal | None) -> dict[str, float | None]:
    if before is None or after is None:
        return {"absolute": None, "percentage": None}
    absolute = float(Decimal(str(after)) - Decimal(str(before)))
    percentage = None if Decimal(str(before)) == 0 else float((Decimal(str(after)) - Decimal(str(before))) * 100 / Decimal(str(before)))
    return {"absolute": absolute, "percentage": percentage}


def compare_reports(before: Report, after: Report) -> dict[str, Any]:
    """Return deltas for every predefined numeric KPI and keyword-set changes."""
    if before.website_id != after.website_id:
        raise ValueError("Reports must belong to the same website.")
    scalar_fields = (
        "health_score", "health_score_delta", "aeo_completion_pct", "aeo_completion_delta", "technical_findings_resolved",
        "technical_findings_open", "content_published_count", "sem_accepted_count",
        "ad_groups_defined_count",
    )
    deltas = {field: _delta(getattr(before, field), getattr(after, field)) for field in scalar_fields}
    for prefix, field, keys in (
        ("sem_cost_tier", "sem_cost_tier_breakdown", ("low", "medium", "high")),
        ("organizer_stage", "organizer_stage_counts", ("backlog", "in_production", "in_review", "published")),
    ):
        old, new = getattr(before, field), getattr(after, field)
        for key in keys:
            deltas[f"{prefix}_{key}"] = _delta(old.get(key, 0), new.get(key, 0))
    old_keywords, new_keywords = set(before.top_keywords), set(after.top_keywords)
    deltas["top_keywords"] = {
        "added": sorted(new_keywords - old_keywords),
        "removed": sorted(old_keywords - new_keywords),
    }
    return deltas
