import enum
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import JSON, Boolean, CheckConstraint, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from trellis.extensions import db


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def enum_type(enum_class: type[enum.Enum], name: str) -> Enum:
    return Enum(enum_class, name=name, native_enum=False, values_callable=lambda choices: [choice.value for choice in choices], validate_strings=True, create_constraint=True)


class AnalysisStatus(str, enum.Enum):
    QUEUED = "queued"
    SCRAPING = "scraping"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class SuggestionCategory(str, enum.Enum):
    AEO = "aeo"
    SEO_CONTENT = "seo_content"
    SEM = "sem"


class SuggestionPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AcceptanceStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DISMISSED = "dismissed"


class DismissReason(str, enum.Enum):
    NOT_RELEVANT = "not_relevant"
    TOO_MUCH_WORK = "too_much_work"
    ALREADY_DOING_THIS = "already_doing_this"
    OTHER = "other"


class CostTier(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SearchIntent(str, enum.Enum):
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    COMMERCIAL = "commercial"
    TRANSACTIONAL = "transactional"


class FindingSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResolutionStatus(str, enum.Enum):
    OPEN = "open"
    RESOLVED = "resolved"


class OrganizerStage(str, enum.Enum):
    BACKLOG = "backlog"
    IN_PRODUCTION = "in_production"
    IN_REVIEW = "in_review"
    PUBLISHED = "published"


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    websites: Mapped[list["Website"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Website(db.Model):
    __tablename__ = "websites"
    __table_args__ = (UniqueConstraint("user_id", "url"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    business_name: Mapped[str] = mapped_column(String(200), nullable=False)
    business_context: Mapped[str | None] = mapped_column(Text)
    google_ads_connected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ga4_connected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    user: Mapped[User] = relationship(back_populates="websites")
    analysis_runs: Mapped[list["AnalysisRun"]] = relationship(back_populates="website", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship(back_populates="website", cascade="all, delete-orphan")
    organizer_items: Mapped[list["OrganizerItem"]] = relationship(back_populates="website", cascade="all, delete-orphan")


class AnalysisRun(db.Model):
    __tablename__ = "analysis_runs"
    __table_args__ = (
        CheckConstraint("health_score IS NULL OR (health_score >= 0 AND health_score <= 100)", name="health_score_range"),
        CheckConstraint("pages_scanned_count >= 0", name="pages_scanned_nonnegative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    website_id: Mapped[int] = mapped_column(ForeignKey("websites.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[AnalysisStatus] = mapped_column(enum_type(AnalysisStatus, "analysis_status"), default=AnalysisStatus.QUEUED, nullable=False)
    pages_scanned_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    health_score: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    website: Mapped[Website] = relationship(back_populates="analysis_runs")
    keywords: Mapped[list["Keyword"]] = relationship(back_populates="analysis_run", cascade="all, delete-orphan")
    suggestions: Mapped[list["Suggestion"]] = relationship(back_populates="analysis_run", cascade="all, delete-orphan")
    technical_findings: Mapped[list["TechnicalFinding"]] = relationship(back_populates="analysis_run", cascade="all, delete-orphan")
    report: Mapped["Report | None"] = relationship(back_populates="analysis_run", uselist=False, cascade="all, delete-orphan")


class Keyword(db.Model):
    __tablename__ = "keywords"
    __table_args__ = (
        UniqueConstraint("analysis_run_id", "phrase"),
        CheckConstraint("frequency >= 0", name="frequency_nonnegative"),
        CheckConstraint("tfidf_score >= 0", name="tfidf_score_nonnegative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    phrase: Mapped[str] = mapped_column(String(500), nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False)
    tfidf_score: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    search_intent: Mapped[SearchIntent | None] = mapped_column(enum_type(SearchIntent, "search_intent"))
    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="keywords")
    suggestion_links: Mapped[list["SuggestionKeyword"]] = relationship(back_populates="keyword", cascade="all, delete-orphan")


class Suggestion(db.Model):
    __tablename__ = "suggestions"
    __table_args__ = (
        CheckConstraint("(acceptance_status = 'dismissed' AND dismiss_reason IS NOT NULL) OR (acceptance_status != 'dismissed' AND dismiss_reason IS NULL)", name="dismiss_reason_matches_status"),
        CheckConstraint("category = 'sem' OR (cost_tier IS NULL AND cpc_low IS NULL AND cpc_high IS NULL AND search_volume IS NULL AND ad_group_label IS NULL AND ad_copy_angle IS NULL AND landing_page_match IS NULL AND targeting_notes IS NULL AND negative_keywords IS NULL)", name="sem_fields_only_for_sem"),
        CheckConstraint("cpc_low IS NULL OR cpc_high IS NULL OR cpc_low <= cpc_high", name="cpc_range_order"),
        CheckConstraint("search_volume IS NULL OR search_volume >= 0", name="search_volume_nonnegative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    affected_page_url: Mapped[str | None] = mapped_column(String(2048))
    category: Mapped[SuggestionCategory] = mapped_column(enum_type(SuggestionCategory, "suggestion_category"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    starter_outline: Mapped[list[str] | None] = mapped_column(JSON)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[SuggestionPriority] = mapped_column(enum_type(SuggestionPriority, "suggestion_priority"), nullable=False)
    acceptance_status: Mapped[AcceptanceStatus] = mapped_column(enum_type(AcceptanceStatus, "acceptance_status"), default=AcceptanceStatus.PENDING, nullable=False)
    dismiss_reason: Mapped[DismissReason | None] = mapped_column(enum_type(DismissReason, "dismiss_reason"))
    cost_tier: Mapped[CostTier | None] = mapped_column(enum_type(CostTier, "cost_tier"))
    cpc_low: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    cpc_high: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    search_volume: Mapped[int | None] = mapped_column(Integer)
    ad_group_label: Mapped[str | None] = mapped_column(String(300))
    ad_copy_angle: Mapped[str | None] = mapped_column(Text)
    landing_page_match: Mapped[str | None] = mapped_column(Text)
    targeting_notes: Mapped[str | None] = mapped_column(Text)
    negative_keywords: Mapped[list[str] | None] = mapped_column(JSON)
    cheaper_alternative_to_id: Mapped[int | None] = mapped_column(ForeignKey("suggestions.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="suggestions")
    cheaper_alternative_to: Mapped["Suggestion | None"] = relationship(remote_side="Suggestion.id")
    keyword_links: Mapped[list["SuggestionKeyword"]] = relationship(back_populates="suggestion", cascade="all, delete-orphan")
    technical_finding_links: Mapped[list["SuggestionTechnicalFinding"]] = relationship(back_populates="suggestion", cascade="all, delete-orphan")
    organizer_item: Mapped["OrganizerItem | None"] = relationship(back_populates="suggestion", uselist=False)


class SuggestionKeyword(db.Model):
    __tablename__ = "suggestion_keywords"
    __table_args__ = (CheckConstraint("recommended_usage_count IS NULL OR recommended_usage_count >= 0", name="recommended_usage_nonnegative"),)

    suggestion_id: Mapped[int] = mapped_column(ForeignKey("suggestions.id", ondelete="CASCADE"), primary_key=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True)
    recommended_usage_count: Mapped[int | None] = mapped_column(Integer)
    suggestion: Mapped[Suggestion] = relationship(back_populates="keyword_links")
    keyword: Mapped[Keyword] = relationship(back_populates="suggestion_links")


class TechnicalFinding(db.Model):
    __tablename__ = "technical_findings"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    affected_page_url: Mapped[str | None] = mapped_column(String(2048))
    related_page_url: Mapped[str | None] = mapped_column(String(2048))
    finding_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[FindingSeverity] = mapped_column(enum_type(FindingSeverity, "finding_severity"), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    resolution_status: Mapped[ResolutionStatus] = mapped_column(enum_type(ResolutionStatus, "resolution_status"), default=ResolutionStatus.OPEN, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="technical_findings")
    suggestion_links: Mapped[list["SuggestionTechnicalFinding"]] = relationship(back_populates="technical_finding", cascade="all, delete-orphan")


class SuggestionTechnicalFinding(db.Model):
    __tablename__ = "suggestion_technical_findings"

    suggestion_id: Mapped[int] = mapped_column(ForeignKey("suggestions.id", ondelete="CASCADE"), primary_key=True)
    technical_finding_id: Mapped[int] = mapped_column(ForeignKey("technical_findings.id", ondelete="CASCADE"), primary_key=True)
    suggestion: Mapped[Suggestion] = relationship(back_populates="technical_finding_links")
    technical_finding: Mapped[TechnicalFinding] = relationship(back_populates="suggestion_links")


class Report(db.Model):
    __tablename__ = "reports"
    __table_args__ = (
        CheckConstraint("health_score >= 0 AND health_score <= 100", name="health_score_range"),
        CheckConstraint("aeo_completion_pct >= 0 AND aeo_completion_pct <= 100", name="aeo_completion_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    website_id: Mapped[int] = mapped_column(ForeignKey("websites.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, unique=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    health_score: Mapped[int] = mapped_column(Integer, nullable=False)
    health_score_delta: Mapped[int | None] = mapped_column(Integer)
    aeo_completion_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    aeo_completion_delta: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    technical_findings_resolved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    technical_findings_open: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    content_published_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    top_keywords: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    sem_accepted_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sem_cost_tier_breakdown: Mapped[dict[str, int]] = mapped_column(JSON, default=dict, nullable=False)
    ad_groups_defined_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    organizer_stage_counts: Mapped[dict[str, int]] = mapped_column(JSON, default=dict, nullable=False)
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    ga4_sessions: Mapped[int | None] = mapped_column(Integer)
    ga4_new_users: Mapped[int | None] = mapped_column(Integer)
    ga4_returning_users: Mapped[int | None] = mapped_column(Integer)
    ga4_conversions: Mapped[int | None] = mapped_column(Integer)
    ga4_revenue: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    real_ad_spend: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    real_roi_pct: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    website: Mapped[Website] = relationship(back_populates="reports")
    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="report")


class OrganizerItem(db.Model):
    __tablename__ = "organizer_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    website_id: Mapped[int] = mapped_column(ForeignKey("websites.id", ondelete="CASCADE"), nullable=False, index=True)
    suggestion_id: Mapped[int | None] = mapped_column(ForeignKey("suggestions.id", ondelete="SET NULL"), unique=True)
    item_type: Mapped[SuggestionCategory] = mapped_column(enum_type(SuggestionCategory, "organizer_item_type"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    stage: Mapped[OrganizerStage] = mapped_column(enum_type(OrganizerStage, "organizer_stage"), default=OrganizerStage.BACKLOG, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    website: Mapped[Website] = relationship(back_populates="organizer_items")
    suggestion: Mapped[Suggestion | None] = relationship(back_populates="organizer_item")
    stage_history: Mapped[list["OrganizerStageHistory"]] = relationship(back_populates="organizer_item", cascade="all, delete-orphan")


class OrganizerStageHistory(db.Model):
    __tablename__ = "organizer_stage_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    organizer_item_id: Mapped[int] = mapped_column(ForeignKey("organizer_items.id", ondelete="CASCADE"), nullable=False, index=True)
    from_stage: Mapped[OrganizerStage | None] = mapped_column(enum_type(OrganizerStage, "organizer_stage_from"))
    to_stage: Mapped[OrganizerStage] = mapped_column(enum_type(OrganizerStage, "organizer_stage_to"), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    organizer_item: Mapped[OrganizerItem] = relationship(back_populates="stage_history")
