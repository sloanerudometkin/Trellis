from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    error: str
    message: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: Literal["trellis-api"]


class WebsiteCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    url: str = Field(min_length=1, max_length=2048)
    business_name: str = Field(min_length=1, max_length=200)
    business_context: str | None = Field(default=None, max_length=5000)


class WebsiteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    business_name: str
    business_context: str | None
    google_ads_connected: bool
    ga4_connected: bool


class KeywordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    phrase: str
    frequency: int
    tfidf_score: float


class SuggestionKeywordResponse(BaseModel):
    phrase: str
    recommended_usage_count: int


class SuggestionResponse(BaseModel):
    id: int
    category: Literal["aeo", "seo_content", "sem"]
    title: str
    description: str
    starter_outline: list[str] | None
    rationale: str
    priority: Literal["low", "medium", "high"]
    status: Literal["pending", "accepted", "dismissed"]
    dismiss_reason: Literal["not_relevant", "too_much_work", "already_doing_this", "other"] | None
    stage: str
    organizer_item_id: int | None
    affected_page_url: str | None
    target_keywords: list[SuggestionKeywordResponse]


class AnalysisRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    website_id: int
    status: Literal["queued", "scraping", "analyzing", "generating", "completed", "failed"]
    last_completed_stage: str | None
    pages_scanned_count: int
    error_message: str | None
    started_at: datetime
    completed_at: datetime | None
    keywords: list[KeywordResponse]
    suggestions: list[SuggestionResponse]


class SuggestionDecisionRequest(BaseModel):
    status: Literal["accepted", "dismissed"]
    dismiss_reason: Literal["not_relevant", "too_much_work", "already_doing_this", "other"] | None = None

    def model_post_init(self, __context) -> None:
        if self.status == "dismissed" and self.dismiss_reason is None:
            raise ValueError("A dismiss reason is required when dismissing a suggestion.")
        if self.status == "accepted" and self.dismiss_reason is not None:
            raise ValueError("An accepted suggestion cannot have a dismiss reason.")


class OrganizerStageRequest(BaseModel):
    stage: Literal["backlog", "in_production", "in_review", "published"]


class OrganizerItemResponse(BaseModel):
    id: int
    website_id: int
    suggestion_id: int | None
    item_type: Literal["aeo", "seo_content", "sem"]
    title: str
    stage: Literal["backlog", "in_production", "in_review", "published"]
    published_at: datetime | None
