from uuid import UUID

import httpx

from conftest import load_json_fixture, load_text_fixture
from trellis.analysis import run_scrape_and_keyword_analysis
from trellis.extensions import db
from trellis.models import AnalysisRun, AnalysisStatus, Keyword, Report, TechnicalFinding, User, Website
from trellis.scraping import clear_crawl_cache


def public_resolver(_hostname: str, port: int):
    return [(2, 1, 6, "", ("93.184.216.34", port))]


def website_record() -> Website:
    user = User(id=UUID("00000000-0000-4000-8000-000000000001"), name="Owner", email="owner@example.com")
    website = Website(user=user, url="https://example.com", business_name="Example")
    db.session.add(user)
    db.session.commit()
    clear_crawl_cache()
    return website


def mock_client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=False)


def test_success_persists_page_count_keywords_and_completed_state(app) -> None:
    website = website_record()

    def handler(request: httpx.Request):
        if request.url.path == "/robots.txt":
            body = load_text_fixture("robots_allow.txt")
        elif request.url.path == "/programs":
            body = "<main>Gardening workshops teach compost soil health and community planting.</main>"
        else:
            body = load_text_fixture("normal_page.html")
        return httpx.Response(200, text=body, headers={"content-type": "text/html"}, request=request)

    with mock_client(handler) as client:
        analysis = run_scrape_and_keyword_analysis(website, client=client, resolver=public_resolver)

    assert analysis.status == AnalysisStatus.COMPLETED
    assert analysis.pages_scanned_count == 2
    assert analysis.completed_at is not None
    assert analysis.report is not None
    assert db.session.scalar(db.select(db.func.count(Report.id)).where(Report.analysis_run_id == analysis.id)) == 1
    assert db.session.scalar(db.select(Keyword).where(Keyword.analysis_run_id == analysis.id)) is not None
    assert "page_snapshots" not in db.metadata.tables
    assert not any("html" in column.name for table in db.metadata.tables.values() for column in table.columns)


def test_timeout_retries_then_saves_failed_state_without_keywords(app) -> None:
    website = website_record()
    attempts = 0

    def handler(request: httpx.Request):
        nonlocal attempts
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=load_text_fixture("robots_allow.txt"), request=request)
        attempts += 1
        raise httpx.ReadTimeout("site timed out", request=request)

    with mock_client(handler) as client:
        analysis = run_scrape_and_keyword_analysis(website, client=client, resolver=public_resolver)

    assert attempts == 3
    assert analysis.status == AnalysisStatus.FAILED
    assert "3 attempts" in analysis.error_message
    assert analysis.keywords == []


def test_transient_timeout_retries_and_completes(app) -> None:
    website = website_record()
    attempts = 0

    def handler(request: httpx.Request):
        nonlocal attempts
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=load_text_fixture("robots_allow.txt"), request=request)
        if request.url.path in {"", "/"}:
            attempts += 1
            if attempts == 1:
                raise httpx.ReadTimeout("temporary timeout", request=request)
        return httpx.Response(200, text=load_text_fixture("duplicate_page.html"), headers={"content-type": "text/html"}, request=request)

    with mock_client(handler) as client:
        analysis = run_scrape_and_keyword_analysis(website, client=client, resolver=public_resolver)

    assert attempts == 2
    assert analysis.status == AnalysisStatus.COMPLETED
    assert analysis.pages_scanned_count == 1
    assert analysis.keywords


def test_partial_failure_keeps_successful_pages_and_keywords(app) -> None:
    website = website_record()

    def handler(request: httpx.Request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=load_text_fixture("robots_allow.txt"), request=request)
        if request.url.path == "/programs":
            return httpx.Response(503, text="unavailable", request=request)
        return httpx.Response(200, text=load_text_fixture("normal_page.html"), headers={"content-type": "text/html"}, request=request)

    with mock_client(handler) as client:
        analysis = run_scrape_and_keyword_analysis(website, client=client, resolver=public_resolver)

    assert analysis.status == AnalysisStatus.COMPLETED
    assert analysis.pages_scanned_count == 1
    assert analysis.keywords
    assert analysis.error_message == "Analysis completed with 1 page request failure(s)."


def test_robots_blocked_site_saves_failure_and_preserves_previous_run(app) -> None:
    website = website_record()
    previous = AnalysisRun(website=website, status=AnalysisStatus.COMPLETED, pages_scanned_count=4)
    previous.keywords.append(Keyword(phrase="existing keyword", frequency=3, tfidf_score=0.8))
    db.session.add(previous)
    db.session.commit()

    def handler(request: httpx.Request):
        return httpx.Response(200, text=load_text_fixture("robots_block.txt"), request=request)

    with mock_client(handler) as client:
        failed = run_scrape_and_keyword_analysis(website, client=client, resolver=public_resolver)

    assert failed.status == AnalysisStatus.FAILED
    assert "robots.txt" in failed.error_message
    assert failed.keywords == []
    assert db.session.get(AnalysisRun, previous.id).keywords[0].phrase == "existing keyword"


def test_analysis_pipeline_persists_local_audit_when_pagespeed_succeeds(app) -> None:
    website = website_record()

    def handler(request: httpx.Request):
        if request.url.host == "www.googleapis.com":
            return httpx.Response(200, json=load_json_fixture("pagespeed_success.json"), request=request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=load_text_fixture("robots_allow.txt"), request=request)
        if request.url.path == "/sitemap.xml":
            return httpx.Response(200, text=load_text_fixture("sitemap_valid.xml"), request=request)
        return httpx.Response(200, text=load_text_fixture("technical_page_violations.html"), headers={"content-type": "text/html"}, request=request)

    with mock_client(handler) as client:
        analysis = run_scrape_and_keyword_analysis(website, client=client, resolver=public_resolver)

    saved = db.session.scalars(
        db.select(TechnicalFinding).where(TechnicalFinding.analysis_run_id == analysis.id)
    ).all()
    assert analysis.status == AnalysisStatus.COMPLETED
    assert {finding.finding_type for finding in saved} >= {
        "title_length", "missing_meta_description", "multiple_h1",
        "heading_order", "missing_image_alt", "thin_content",
    }
