"""Deterministic, non-transactional SEM planning built from existing site data."""

from __future__ import annotations

from dataclasses import dataclass

from trellis.models import CostTier, Keyword, Suggestion, SuggestionCategory, SuggestionKeyword, SuggestionPriority


COST_TIER_DISCLOSURE = "Heuristic estimate based on keyword shape and intent—not live Google Ads bid data."
CAMPAIGN_BOUNDARY = "Planning only: Trellis cannot create, launch, manage, bid on, or spend money on advertising campaigns."
COMMERCIAL_MODIFIERS = {"buy", "hire", "pricing", "price", "quote", "best", "services", "service", "near me"}
COMMON_NEGATIVES = ("free", "jobs", "DIY", "how to")


@dataclass(frozen=True)
class SemCandidate:
    keyword: Keyword
    cost_tier: CostTier
    commercial_intent: bool


def has_commercial_intent(phrase: str) -> bool:
    normalized = " ".join(phrase.casefold().split())
    tokens = set(normalized.split())
    return "near me" in normalized or bool(tokens & (COMMERCIAL_MODIFIERS - {"near me"}))


def infer_cost_tier(phrase: str) -> CostTier:
    """Use keyword length as a transparent relative-cost proxy for MVP."""
    word_count = len(phrase.split())
    if word_count >= 3:
        return CostTier.LOW
    if word_count == 2:
        return CostTier.MEDIUM
    return CostTier.HIGH


def rank_sem_candidates(keywords: list[Keyword], limit: int = 4) -> list[SemCandidate]:
    candidates = [SemCandidate(keyword, infer_cost_tier(keyword.phrase), has_commercial_intent(keyword.phrase)) for keyword in keywords]
    tier_order = {CostTier.LOW: 0, CostTier.MEDIUM: 1, CostTier.HIGH: 2}
    return sorted(candidates, key=lambda item: (
        not item.commercial_intent,
        tier_order[item.cost_tier],
        -float(item.keyword.tfidf_score),
        -item.keyword.frequency,
        item.keyword.phrase,
    ))[:limit]


def cheaper_alternatives(phrase: str) -> list[str]:
    if infer_cost_tier(phrase) == CostTier.LOW:
        return []
    normalized = " ".join(phrase.casefold().split())
    options = [f"affordable {normalized} services", f"{normalized} near me", f"best local {normalized}"]
    return list(dict.fromkeys(option for option in options if infer_cost_tier(option) == CostTier.LOW))[:3]


def is_local_business(context: str | None) -> bool:
    value = (context or "").casefold()
    return any(signal in value for signal in ("local", "neighborhood", "nearby", "city", "town", "service area"))


def targeting_guidance(context: str | None) -> str:
    if is_local_business(context):
        return "Use the Google Search network for high-intent searches; target relevant service interests within about 15 miles of the local service area."
    return "Use the Google Search network for high-intent searches; target audiences actively researching this topic in the business’s served region."


def negative_keywords(analysis_keywords: list[Keyword], context: str | None) -> list[str]:
    context_text = (context or "").casefold()
    surfaced_text = " ".join(keyword.phrase for keyword in analysis_keywords).casefold()
    surfaced = [term for term in COMMON_NEGATIVES if term.casefold() in surfaced_text and term.casefold() not in context_text]
    remaining = [term for term in COMMON_NEGATIVES if term.casefold() not in context_text and term not in surfaced]
    return surfaced + remaining


def landing_page_for(analysis, phrase: str) -> str:
    tokens = set(phrase.casefold().split())
    suggestions = [item for item in analysis.suggestions if item.category != SuggestionCategory.SEM and item.affected_page_url]
    matching = [item for item in suggestions if tokens & set(f"{item.title} {item.description}".casefold().split())]
    return (matching[0] if matching else suggestions[0]).affected_page_url if (matching or suggestions) else analysis.website.url


def apply_sem_strategy(analysis) -> None:
    """Normalize generated SEM suggestions and add cheaper linked alternatives."""
    seeds = [item for item in analysis.suggestions if item.category == SuggestionCategory.SEM]
    candidates = rank_sem_candidates(list(analysis.keywords))
    if not seeds or not candidates:
        return
    template = seeds[0]
    for extra in seeds:
        analysis.suggestions.remove(extra)
    shared_negatives = negative_keywords(list(analysis.keywords), analysis.website.business_context)
    shared_targeting = targeting_guidance(analysis.website.business_context)

    for index, candidate in enumerate(candidates[:4]):
        phrase = candidate.keyword.phrase
        primary = template if index == 0 else Suggestion(
            category=SuggestionCategory.SEM,
            title=f"Test the keyword: {phrase}",
            description=f"Create a tightly matched search ad group centered on “{phrase}”.",
            rationale="Temporary rationale replaced below.",
            priority=SuggestionPriority.HIGH if candidate.commercial_intent else SuggestionPriority.MEDIUM,
            affected_page_url=template.affected_page_url,
        )
        primary.cost_tier = candidate.cost_tier
        primary.ad_group_label = f"{phrase.title()} intent"
        primary.ad_copy_angle = f"Lead with the specific outcome behind “{phrase}” and a clear next step."
        primary.landing_page_match = landing_page_for(analysis, phrase)
        primary.targeting_notes = shared_targeting
        primary.negative_keywords = list(shared_negatives)
        primary.rationale = f"Keep “{phrase}” in a tightly themed ad group because close keyword, ad, and landing-page alignment supports Quality Score and helps control CPC."
        primary.keyword_links.append(SuggestionKeyword(keyword=candidate.keyword, recommended_usage_count=None))
        analysis.suggestions.append(primary)

        for alternative_phrase in cheaper_alternatives(phrase):
            analysis.suggestions.append(Suggestion(
                category=SuggestionCategory.SEM,
                title=f"Try the lower-cost keyword: {alternative_phrase}",
                description=f"Test “{alternative_phrase}” as a more specific alternative to “{phrase}”.",
                rationale=f"This longer phrase keeps the same intent while receiving a lower heuristic Cost Tier than the broader “{phrase}” term.",
                priority=SuggestionPriority.HIGH if has_commercial_intent(alternative_phrase) else SuggestionPriority.MEDIUM,
                affected_page_url=primary.affected_page_url,
                cost_tier=CostTier.LOW,
                ad_group_label=primary.ad_group_label,
                ad_copy_angle=primary.ad_copy_angle,
                landing_page_match=primary.landing_page_match,
                targeting_notes=primary.targeting_notes,
                negative_keywords=list(primary.negative_keywords or []),
                cheaper_alternative_to=primary,
            ))
