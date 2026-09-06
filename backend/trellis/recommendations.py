"""Prompt, provider fallback, validation, and persistence for recommendations."""

from __future__ import annotations

import json
import re
from collections.abc import Callable

import httpx
from pydantic import ValidationError
from sqlalchemy import null

from trellis.extensions import db
from trellis.models import AcceptanceStatus, AnalysisRun, Suggestion, SuggestionKeyword
from trellis.recommendation_schemas import RecommendationBatch


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
SYSTEM_PROMPT = """You are Trellis, a paid-and-organic search strategist for resource-limited marketers. Return only JSON matching the supplied schema. Give site-specific AEO, SEO/content, and SEM recommendations. Every rationale must explain why the action matters for this website. SEM cost tiers are heuristic estimates, never real bid prices."""


class RecommendationProviderError(RuntimeError):
    pass


class RecommendationRateLimitError(RecommendationProviderError):
    pass


EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE = re.compile(r"(?<!\d)(?:\+?1[ .-]?)?(?:\(?\d{3}\)?[ .-]?)\d{3}[ .-]?\d{4}(?!\d)")
SSN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")


def remove_pii(value: str) -> str:
    cleaned = EMAIL.sub("[redacted email]", value)
    cleaned = PHONE.sub("[redacted phone]", cleaned)
    return SSN.sub("[redacted identifier]", cleaned)


def build_recommendation_prompt(analysis: AnalysisRun) -> str:
    website = analysis.website
    context = remove_pii(website.business_context or "No additional business context provided.")
    keywords = ", ".join(keyword.phrase for keyword in analysis.keywords[:30])
    prompt = (
        f"Website: {website.url}\n"
        f"Business: {remove_pii(website.business_name)}\n"
        f"Business context: {context}\n"
        f"Pages analyzed: {analysis.pages_scanned_count}\n"
        f"Ranked site keywords: {keywords}\n\n"
        "Produce a balanced batch containing AEO, SEO/content, and SEM actions. "
        "Use only the supplied site evidence; do not invent private facts. "
        "For each SEO/content action, select target keyword phrases exactly from the ranked site keywords and give a realistic recommended usage count.\n"
        f"Required JSON schema: {json.dumps(RecommendationBatch.model_json_schema(), separators=(',', ':'))}"
    )
    return remove_pii(prompt)


def _groq_content(client: httpx.Client, prompt: str, api_key: str) -> str:
    response = client.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        },
    )
    if response.status_code == 429:
        raise RecommendationRateLimitError("Groq is temporarily rate limited.")
    if response.status_code >= 500:
        raise RecommendationProviderError("Groq is temporarily unavailable.")
    response.raise_for_status()
    try:
        return response.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise RecommendationProviderError("Groq returned an unexpected response.") from error


def _gemini_content(client: httpx.Client, prompt: str, api_key: str) -> str:
    response = client.post(
        GEMINI_URL,
        params={"key": api_key},
        json={
            "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\n{prompt}"}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseJsonSchema": RecommendationBatch.model_json_schema(),
                "temperature": 0.2,
            },
        },
    )
    if response.status_code == 429:
        raise RecommendationRateLimitError("Gemini is temporarily rate limited.")
    if response.status_code >= 500:
        raise RecommendationProviderError("Gemini is temporarily unavailable.")
    response.raise_for_status()
    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as error:
        raise RecommendationProviderError("Gemini returned an unexpected response.") from error


def _validate_content(content: str) -> RecommendationBatch:
    return RecommendationBatch.model_validate(json.loads(content))


def generate_recommendations(prompt: str, *, client: httpx.Client, groq_api_key: str, gemini_api_key: str) -> RecommendationBatch:
    """Use Groq first, retry schema drift once, then use Gemini as backup."""
    providers: list[tuple[str, Callable[[], str]]] = []
    if groq_api_key:
        providers.append(("Groq", lambda: _groq_content(client, prompt, groq_api_key)))
    if gemini_api_key:
        providers.append(("Gemini", lambda: _gemini_content(client, prompt, gemini_api_key)))
    if not providers:
        raise RecommendationProviderError("No recommendation provider is configured.")

    errors: list[str] = []
    for provider_name, request_content in providers:
        for validation_attempt in range(2):
            try:
                return _validate_content(request_content())
            except (json.JSONDecodeError, ValidationError):
                errors.append(f"{provider_name} returned invalid structured output.")
                if validation_attempt == 0:
                    continue
            except (RecommendationProviderError, httpx.HTTPError) as error:
                errors.append(str(error))
                break
    raise RecommendationProviderError(" ".join(errors))


def persist_recommendations(analysis: AnalysisRun, batch: RecommendationBatch) -> None:
    keywords_by_phrase = {keyword.phrase.casefold(): keyword for keyword in analysis.keywords}
    try:
        analysis.suggestions.clear()
        db.session.flush()
        for item in batch.suggestions:
            suggestion = Suggestion(
                category=item.category,
                title=item.title,
                description=item.description,
                starter_outline=item.starter_outline,
                rationale=item.rationale,
                priority=item.priority,
                affected_page_url=str(item.affected_page_url) if item.affected_page_url else None,
                acceptance_status=AcceptanceStatus.PENDING,
                cost_tier=item.cost_tier,
                ad_group_label=item.ad_group_guidance,
                landing_page_match=item.landing_page_fit,
                targeting_notes=item.targeting_notes,
                negative_keywords=item.negative_keywords if item.category == "sem" else null(),
            )
            for target in item.target_keywords or []:
                keyword = keywords_by_phrase.get(target.phrase.casefold())
                if keyword is None:
                    raise ValueError(f"Recommendation target keyword was not found in the analysis: {target.phrase}")
                suggestion.keyword_links.append(SuggestionKeyword(
                    keyword=keyword,
                    recommended_usage_count=target.recommended_usage_count,
                ))
            analysis.suggestions.append(suggestion)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def generate_and_persist_recommendations(
    analysis: AnalysisRun,
    *,
    client: httpx.Client,
    groq_api_key: str,
    gemini_api_key: str,
) -> None:
    prompt = build_recommendation_prompt(analysis)
    batch = generate_recommendations(
        prompt,
        client=client,
        groq_api_key=groq_api_key,
        gemini_api_key=gemini_api_key,
    )
    persist_recommendations(analysis, batch)
