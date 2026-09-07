"""Deterministic technical SEO checks for one bounded Trellis crawl."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin
from xml.etree import ElementTree

import httpx
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from trellis.extensions import db
from trellis.models import AnalysisRun, FindingSeverity, TechnicalFinding
from trellis.scraping import CrawlResult, ScrapedPage, USER_AGENT


PAGESPEED_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
THIN_CONTENT_WORDS = 100
NEAR_DUPLICATE_THRESHOLD = 0.85
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


@dataclass(frozen=True)
class PageSpeedResult:
    performance_score: int | None = None
    largest_contentful_paint_ms: float | None = None
    cumulative_layout_shift: float | None = None
    interaction_to_next_paint_ms: float | None = None
    error: str | None = None


@dataclass(frozen=True)
class AuditFinding:
    finding_type: str
    severity: FindingSeverity
    explanation: str
    affected_page_url: str | None = None
    related_page_url: str | None = None


def fetch_pagespeed(client: httpx.Client, url: str, api_key: str = "") -> PageSpeedResult:
    """Return mobile PageSpeed measurements or a safe, user-facing failure."""
    params = {"url": url, "strategy": "mobile", "category": "performance"}
    if api_key:
        params["key"] = api_key
    try:
        response = client.get(PAGESPEED_URL, params=params)
    except httpx.TimeoutException:
        return PageSpeedResult(error="PageSpeed timed out; the local audit still completed.")
    except httpx.HTTPError:
        return PageSpeedResult(error="PageSpeed was unavailable; the local audit still completed.")
    if response.status_code == 429:
        return PageSpeedResult(error="PageSpeed quota was reached; the local audit still completed.")
    if response.status_code >= 400:
        return PageSpeedResult(error=f"PageSpeed returned HTTP {response.status_code}; the local audit still completed.")
    try:
        lighthouse = response.json()["lighthouseResult"]
        audits = lighthouse["audits"]
        score = lighthouse["categories"]["performance"]["score"]
        return PageSpeedResult(
            performance_score=round(float(score) * 100),
            largest_contentful_paint_ms=float(audits["largest-contentful-paint"]["numericValue"]),
            cumulative_layout_shift=float(audits["cumulative-layout-shift"]["numericValue"]),
            interaction_to_next_paint_ms=float(audits["interaction-to-next-paint"]["numericValue"]),
        )
    except (KeyError, TypeError, ValueError):
        return PageSpeedResult(error="PageSpeed returned an unreadable response; the local audit still completed.")


def pagespeed_findings(result: PageSpeedResult, url: str) -> list[AuditFinding]:
    if result.error:
        return [AuditFinding("pagespeed_unavailable", FindingSeverity.LOW, result.error, url)]
    findings: list[AuditFinding] = []
    if result.performance_score is not None and result.performance_score < 90:
        findings.append(AuditFinding("mobile_performance", FindingSeverity.HIGH if result.performance_score < 50 else FindingSeverity.MEDIUM, f"Mobile performance scored {result.performance_score}/100. Improve the slowest page resources first.", url))
    if result.largest_contentful_paint_ms is not None and result.largest_contentful_paint_ms > 2500:
        findings.append(AuditFinding("largest_contentful_paint", FindingSeverity.HIGH, f"Largest Contentful Paint was {round(result.largest_contentful_paint_ms)} ms; aim for 2,500 ms or less.", url))
    if result.cumulative_layout_shift is not None and result.cumulative_layout_shift > 0.1:
        findings.append(AuditFinding("cumulative_layout_shift", FindingSeverity.MEDIUM, f"Cumulative Layout Shift was {result.cumulative_layout_shift:.2f}; aim for 0.10 or less.", url))
    if result.interaction_to_next_paint_ms is not None and result.interaction_to_next_paint_ms > 200:
        findings.append(AuditFinding("interaction_to_next_paint", FindingSeverity.MEDIUM, f"Interaction to Next Paint was {round(result.interaction_to_next_paint_ms)} ms; aim for 200 ms or less.", url))
    return findings


def page_findings(page: ScrapedPage) -> list[AuditFinding]:
    soup = BeautifulSoup(page.html, "html.parser")
    findings: list[AuditFinding] = []
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    if not title:
        findings.append(AuditFinding("missing_title", FindingSeverity.HIGH, "Add a unique page title so search engines and visitors can identify this page.", page.url))
    elif not 30 <= len(title) <= 60:
        findings.append(AuditFinding("title_length", FindingSeverity.MEDIUM, f"The page title is {len(title)} characters; use a clear title around 30–60 characters.", page.url))
    description = soup.find("meta", attrs={"name": lambda value: value and value.lower() == "description"})
    description_text = str(description.get("content", "")).strip() if description else ""
    if not description_text:
        findings.append(AuditFinding("missing_meta_description", FindingSeverity.MEDIUM, "Add a specific meta description that explains why someone should visit this page.", page.url))
    h1s = soup.find_all("h1")
    if not h1s:
        findings.append(AuditFinding("missing_h1", FindingSeverity.HIGH, "Add one clear H1 heading that states the page’s main topic.", page.url))
    elif len(h1s) > 1:
        findings.append(AuditFinding("multiple_h1", FindingSeverity.MEDIUM, f"This page has {len(h1s)} H1 headings; keep one primary H1 and use H2/H3 for sections.", page.url))
    levels = [int(heading.name[1]) for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
    if any(current - previous > 1 for previous, current in zip(levels, levels[1:])):
        findings.append(AuditFinding("heading_order", FindingSeverity.MEDIUM, "Heading levels skip a step; use a logical H1 → H2 → H3 structure.", page.url))
    missing_alt = [image for image in soup.find_all("img") if image.get("alt") is None or not str(image.get("alt")).strip()]
    if missing_alt:
        findings.append(AuditFinding("missing_image_alt", FindingSeverity.MEDIUM, f"Add useful alt text to {len(missing_alt)} image(s) so their meaning is accessible and understandable.", page.url))
    if len(page.text.split()) < THIN_CONTENT_WORDS:
        findings.append(AuditFinding("thin_content", FindingSeverity.MEDIUM, f"This page has about {len(page.text.split())} readable words; add useful, original detail where it serves the visitor.", page.url))
    return findings


def duplicate_findings(pages: list[ScrapedPage]) -> list[AuditFinding]:
    if len(pages) < 2:
        return []
    findings: list[AuditFinding] = []
    normalized = [" ".join(page.text.lower().split()) for page in pages]
    for left in range(len(pages)):
        for right in range(left + 1, len(pages)):
            if normalized[left] == normalized[right]:
                findings.append(AuditFinding("duplicate_content", FindingSeverity.HIGH, "These pages contain the same readable content; consolidate them or make each page serve a distinct purpose.", pages[left].url, pages[right].url))
    try:
        matrix = TfidfVectorizer(stop_words="english").fit_transform(normalized)
    except ValueError:
        # Pages containing only stop words have no meaningful vocabulary to
        # compare, so they cannot support a near-duplicate conclusion.
        return findings
    similarities = cosine_similarity(matrix)
    for left in range(len(pages)):
        for right in range(left + 1, len(pages)):
            score = float(similarities[left, right])
            if normalized[left] != normalized[right] and score >= NEAR_DUPLICATE_THRESHOLD:
                findings.append(AuditFinding("near_duplicate_content", FindingSeverity.HIGH, f"These pages are {round(score * 100)}% similar; combine overlapping material or clarify their different search intent.", pages[left].url, pages[right].url))
    return findings


def resource_findings(client: httpx.Client, root_url: str) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    for filename, finding_type, label in [("robots.txt", "robots_invalid", "robots.txt"), ("sitemap.xml", "sitemap_invalid", "sitemap.xml")]:
        url = urljoin(root_url.rstrip("/") + "/", filename)
        try:
            response = client.get(url, headers={"User-Agent": USER_AGENT})
            if response.status_code != 200:
                findings.append(AuditFinding(finding_type, FindingSeverity.HIGH if filename == "robots.txt" else FindingSeverity.MEDIUM, f"{label} is missing or unavailable (HTTP {response.status_code}).", url))
            elif filename == "robots.txt" and "user-agent:" not in response.text.lower():
                findings.append(AuditFinding(finding_type, FindingSeverity.HIGH, "robots.txt is present but does not contain a valid User-agent rule.", url))
            elif filename == "sitemap.xml":
                try:
                    root_name = ElementTree.fromstring(response.text).tag.rsplit("}", 1)[-1]
                except ElementTree.ParseError:
                    root_name = ""
                if root_name not in {"urlset", "sitemapindex"}:
                    findings.append(AuditFinding(finding_type, FindingSeverity.MEDIUM, "sitemap.xml is present but is not a valid URL set or sitemap index.", url))
        except httpx.HTTPError:
            findings.append(AuditFinding(finding_type, FindingSeverity.LOW, f"Trellis could not verify {label}; the remaining audit still completed.", url))
    return findings


def run_technical_audit(crawl: CrawlResult, root_url: str, *, client: httpx.Client, pagespeed_api_key: str = "") -> list[AuditFinding]:
    findings = pagespeed_findings(fetch_pagespeed(client, root_url, pagespeed_api_key), root_url)
    findings.extend(resource_findings(client, root_url))
    findings.extend(AuditFinding("crawl_error", FindingSeverity.HIGH, "This page returned an error while Trellis crawled the site. Check the URL and server response.", url) for url in crawl.failed_urls)
    for page in crawl.pages:
        findings.extend(page_findings(page))
    findings.extend(duplicate_findings(crawl.pages))
    return sorted(findings, key=lambda item: (SEVERITY_ORDER[item.severity.value], item.finding_type, item.affected_page_url or ""))


def persist_technical_findings(analysis: AnalysisRun, findings: list[AuditFinding]) -> None:
    analysis.technical_findings.clear()
    db.session.flush()
    analysis.technical_findings.extend(TechnicalFinding(
        finding_type=finding.finding_type,
        severity=finding.severity,
        explanation=finding.explanation,
        affected_page_url=finding.affected_page_url,
        related_page_url=finding.related_page_url,
    ) for finding in findings)
    db.session.commit()


def build_fix_first_summary(findings: list[TechnicalFinding] | list[AuditFinding]) -> str:
    if not findings:
        return "No technical SEO problems were found in this bounded audit. Keep monitoring the site as it changes."
    ordered = sorted(findings, key=lambda item: (SEVERITY_ORDER[item.severity.value], item.finding_type))
    first = ordered[0]
    return f"Fix first: {first.explanation} Trellis found {len(findings)} prioritized technical item{'s' if len(findings) != 1 else ''} in this scan."
