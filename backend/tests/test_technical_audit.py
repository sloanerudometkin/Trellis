import httpx
import uuid

from conftest import load_json_fixture, load_text_fixture
from trellis.extensions import db
from trellis.models import AnalysisRun, AnalysisStatus, FindingSeverity, User, Website
from trellis.scraping import CrawlResult, ScrapedPage, clear_crawl_cache, crawl_site, extract_text
from trellis.technical_audit import (
    NEAR_DUPLICATE_THRESHOLD,
    build_fix_first_summary,
    duplicate_findings,
    fetch_pagespeed,
    page_findings,
    persist_technical_findings,
    pagespeed_findings,
    resource_findings,
    run_technical_audit,
)


def page(fixture: str, url: str) -> ScrapedPage:
    html = load_text_fixture(fixture)
    return ScrapedPage(url=url, text=extract_text(html), html=html)


def client_for(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_pagespeed_success_reads_mobile_score_and_core_web_vitals():
    def handler(request):
        assert request.url.params["strategy"] == "mobile"
        return httpx.Response(200, json=load_json_fixture("pagespeed_success.json"), request=request)

    result = fetch_pagespeed(client_for(handler), "https://example.com", "test-key")

    assert result.performance_score == 91
    assert result.largest_contentful_paint_ms == 1800
    assert result.cumulative_layout_shift == 0.05
    assert result.interaction_to_next_paint_ms == 160
    assert result.error is None


def test_pagespeed_timeout_is_a_graceful_result():
    def handler(request):
        raise httpx.ReadTimeout("slow", request=request)

    assert "timed out" in fetch_pagespeed(client_for(handler), "https://example.com").error


def test_pagespeed_quota_is_a_graceful_result():
    def handler(request):
        return httpx.Response(429, json=load_json_fixture("pagespeed_quota.json"), request=request)

    assert "quota" in fetch_pagespeed(client_for(handler), "https://example.com").error


def test_pagespeed_malformed_response_is_a_graceful_result():
    def handler(request):
        return httpx.Response(200, json=load_json_fixture("pagespeed_malformed.json"), request=request)

    assert "unreadable" in fetch_pagespeed(client_for(handler), "https://example.com").error


def test_pagespeed_thresholds_create_mobile_and_core_web_vital_findings():
    def handler(request):
        return httpx.Response(200, json=load_json_fixture("pagespeed_slow.json"), request=request)
    result = fetch_pagespeed(client_for(handler), "https://example.com")
    assert {item.finding_type for item in pagespeed_findings(result, "https://example.com")} == {
        "mobile_performance", "largest_contentful_paint",
        "cumulative_layout_shift", "interaction_to_next_paint",
    }


def test_metadata_headings_alt_text_and_thin_content_rules_use_fixed_fixture():
    findings = page_findings(page("technical_page_violations.html", "https://example.com/bad"))
    types = {finding.finding_type for finding in findings}

    assert types == {
        "title_length", "missing_meta_description", "multiple_h1",
        "heading_order", "missing_image_alt", "thin_content",
    }


def test_valid_page_passes_all_local_page_rules():
    assert page_findings(page("technical_page_valid.html", "https://example.com/good")) == []


def test_missing_title_and_h1_are_reported():
    types = {item.finding_type for item in page_findings(
        page("technical_page_missing_structure.html", "https://example.com/unstructured")
    )}
    assert {"missing_title", "missing_h1"} <= types


def test_sitemap_and_robots_missing_and_malformed_rules():
    def missing(request):
        return httpx.Response(404, request=request)
    missing_types = {item.finding_type for item in resource_findings(client_for(missing), "https://example.com")}
    assert missing_types == {"robots_invalid", "sitemap_invalid"}

    def malformed(request):
        body = load_text_fixture("robots_malformed.txt") if request.url.path.endswith("robots.txt") else load_text_fixture("sitemap_malformed.xml")
        return httpx.Response(200, text=body, request=request)
    malformed_types = {item.finding_type for item in resource_findings(client_for(malformed), "https://example.com")}
    assert malformed_types == {"robots_invalid", "sitemap_invalid"}


def test_duplicate_content_rule_flags_exact_match():
    first = page("technical_page_valid.html", "https://example.com/one")
    second = ScrapedPage(url="https://example.com/two", text=first.text, html=first.html)
    findings = duplicate_findings([first, second])
    assert [finding.finding_type for finding in findings] == ["duplicate_content"]


def test_tfidf_similarity_flags_near_duplicate_above_threshold():
    findings = duplicate_findings([
        page("technical_page_near_duplicate_a.html", "https://example.com/a"),
        page("technical_page_near_duplicate_b.html", "https://example.com/b"),
    ])
    near_duplicate = next(item for item in findings if item.finding_type == "near_duplicate_content")
    percentage = int(near_duplicate.explanation.split("%", 1)[0].rsplit(" ", 1)[-1])
    assert percentage / 100 >= NEAR_DUPLICATE_THRESHOLD


def test_tfidf_similarity_does_not_flag_distinct_pages():
    assert not any(item.finding_type == "near_duplicate_content" for item in duplicate_findings([
        page("technical_page_near_duplicate_a.html", "https://example.com/a"),
        page("technical_page_valid.html", "https://example.com/good"),
    ]))


def test_tfidf_similarity_handles_pages_with_no_meaningful_vocabulary():
    pages = [
        ScrapedPage("https://example.com/a", "the and or", "<p>the and or</p>"),
        ScrapedPage("https://example.com/b", "and the but", "<p>and the but</p>"),
    ]
    assert duplicate_findings(pages) == []


def test_crawl_errors_are_prioritized_and_pagespeed_failure_does_not_erase_local_audit():
    def handler(request):
        if request.url.host == "www.googleapis.com":
            return httpx.Response(429, request=request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=load_text_fixture("robots_allow.txt"), request=request)
        return httpx.Response(200, text=load_text_fixture("sitemap_valid.xml"), request=request)
    crawl = CrawlResult(
        pages=[page("technical_page_violations.html", "https://example.com/bad")],
        failed_urls=["https://example.com/broken"],
    )

    findings = run_technical_audit(crawl, "https://example.com", client=client_for(handler))
    types = {item.finding_type for item in findings}

    assert "pagespeed_unavailable" in types
    assert "crawl_error" in types
    assert "missing_meta_description" in types
    assert findings[0].severity in {FindingSeverity.HIGH, FindingSeverity.CRITICAL}


def test_404_and_500_crawl_failures_each_become_findings():
    crawl = CrawlResult(
        pages=[page("technical_page_valid.html", "https://example.com/")],
        failed_urls=["https://example.com/missing", "https://example.com/server-error"],
    )
    def handler(request):
        if request.url.host == "www.googleapis.com":
            return httpx.Response(200, json=load_json_fixture("pagespeed_success.json"), request=request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=load_text_fixture("robots_allow.txt"), request=request)
        return httpx.Response(200, text=load_text_fixture("sitemap_valid.xml"), request=request)
    findings = run_technical_audit(crawl, "https://example.com", client=client_for(handler))
    crawl_findings = [item for item in findings if item.finding_type == "crawl_error"]
    assert [item.affected_page_url for item in crawl_findings] == [
        "https://example.com/missing", "https://example.com/server-error",
    ]


def test_crawler_records_both_404_and_500_responses_for_the_audit():
    clear_crawl_cache()
    def handler(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=load_text_fixture("robots_allow.txt"), request=request)
        if request.url.path == "/missing":
            return httpx.Response(404, text=load_text_fixture("crawl_error_404.html"), request=request)
        if request.url.path == "/server-error":
            return httpx.Response(500, text=load_text_fixture("crawl_error_500.html"), request=request)
        return httpx.Response(200, text=load_text_fixture("technical_crawl_root.html"), headers={"content-type": "text/html"}, request=request)

    crawl = crawl_site(
        "https://example.com",
        client=client_for(handler),
        resolver=lambda _hostname, port: [(2, 1, 6, "", ("93.184.216.34", port))],
        retries=0,
        cache_ttl_seconds=0,
    )

    assert crawl.failed_urls == [
        "https://example.com/missing", "https://example.com/server-error",
    ]


def test_findings_persist_and_summary_leads_with_highest_priority(app):
    with app.app_context():
        user = User(id=uuid.UUID("00000000-0000-4000-8000-000000000001"), name="One", email="one@example.com")
        website = Website(user=user, url="https://example.com", business_name="Example")
        analysis = AnalysisRun(website=website, status=AnalysisStatus.ANALYZING)
        db.session.add(analysis)
        db.session.commit()
        audit = page_findings(page("technical_page_violations.html", "https://example.com/bad"))

        persist_technical_findings(analysis, audit)

        assert len(analysis.technical_findings) == len(audit)
        summary = build_fix_first_summary(analysis.technical_findings)
        assert summary.startswith("Fix first:")
        assert "H1" in summary
