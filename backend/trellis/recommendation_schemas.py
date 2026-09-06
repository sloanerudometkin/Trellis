"""Strict contracts for structured LLM recommendation output."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class TargetKeywordOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    phrase: str = Field(min_length=2, max_length=500)
    recommended_usage_count: int = Field(ge=1, le=100)


class RecommendationOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    category: Literal["aeo", "seo_content", "sem"]
    title: str = Field(min_length=5, max_length=300)
    description: str = Field(min_length=10, max_length=3000)
    rationale: str = Field(min_length=15, max_length=1000)
    priority: Literal["low", "medium", "high"]
    affected_page_url: HttpUrl | None = None
    starter_outline: list[str] | None = Field(default=None, max_length=12)
    target_keywords: list[TargetKeywordOutput] | None = Field(default=None, min_length=1, max_length=10)
    cost_tier: Literal["low", "medium", "high"] | None = None
    ad_group_guidance: str | None = Field(default=None, max_length=300)
    landing_page_fit: str | None = Field(default=None, max_length=2000)
    targeting_notes: str | None = Field(default=None, max_length=2000)
    negative_keywords: list[str] | None = Field(default=None, max_length=30)
    status: Literal["pending"] = "pending"
    stage: Literal["suggested"] = "suggested"

    @model_validator(mode="after")
    def validate_category_fields(self):
        if self.category == "seo_content":
            if not self.starter_outline:
                raise ValueError("SEO/content recommendations require a starter outline.")
            if not self.target_keywords:
                raise ValueError("SEO/content recommendations require target keywords and usage counts.")
            phrases = [keyword.phrase.casefold() for keyword in self.target_keywords]
            if len(phrases) != len(set(phrases)):
                raise ValueError("SEO/content target keywords must be unique.")
        elif self.target_keywords:
            raise ValueError("Target keywords are allowed only for SEO/content recommendations.")
        if self.category == "sem":
            required = [self.cost_tier, self.ad_group_guidance, self.landing_page_fit, self.targeting_notes]
            if any(value is None for value in required):
                raise ValueError("SEM recommendations require cost, ad group, landing page, and targeting guidance.")
        elif any([self.cost_tier, self.ad_group_guidance, self.landing_page_fit, self.targeting_notes, self.negative_keywords]):
            raise ValueError("Paid-search fields are allowed only for SEM recommendations.")
        return self


class RecommendationBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suggestions: list[RecommendationOutput] = Field(min_length=1, max_length=30)

    @model_validator(mode="after")
    def include_paid_and_organic_categories(self):
        categories = {suggestion.category for suggestion in self.suggestions}
        if categories != {"aeo", "seo_content", "sem"}:
            raise ValueError("The response must include AEO, SEO/content, and SEM recommendations.")
        return self
