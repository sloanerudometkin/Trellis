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
