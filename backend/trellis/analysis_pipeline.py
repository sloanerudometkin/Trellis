"""Persistent, restartable stages for the Trellis analysis pipeline."""
from __future__ import annotations
import socket
from collections.abc import Callable
from decimal import Decimal
import httpx
from trellis.extensions import db
from trellis.keywords import extract_keywords
from trellis.models import AnalysisRun, AnalysisStatus, Keyword, Website, utc_now
from trellis.scraping import CrawlError, crawl_site
from trellis.technical_audit import persist_technical_findings, run_technical_audit
from trellis.health_score import persist_health_score

StageHook = Callable[[AnalysisStatus, AnalysisRun], None]
RecommendationGenerator = Callable[[AnalysisRun], None]

def create_analysis_run(website: Website) -> AnalysisRun:
    analysis = AnalysisRun(website=website, status=AnalysisStatus.QUEUED)
    db.session.add(analysis)
    db.session.commit()
    return analysis

def _enter_stage(analysis: AnalysisRun, status: AnalysisStatus, hook: StageHook | None) -> None:
    analysis.status = status
    analysis.completed_at = None
    db.session.commit()
    if hook:
        hook(status, analysis)

def execute_analysis_run(analysis: AnalysisRun, *, client: httpx.Client | None = None, resolver=socket.getaddrinfo, stage_hook: StageHook | None = None, recommendation_generator: RecommendationGenerator | None = None, pagespeed_api_key: str = "") -> AnalysisRun:
    """Execute or resume a run from its last durable completed stage."""
    if analysis.status == AnalysisStatus.COMPLETED:
        return analysis
    if analysis.status == AnalysisStatus.FAILED:
        analysis.error_message = None
        db.session.commit()
    owns_client = client is None
    request_client = client or httpx.Client(timeout=httpx.Timeout(10.0), follow_redirects=False)
    try:
        if analysis.last_completed_stage not in {AnalysisStatus.ANALYZING.value, AnalysisStatus.GENERATING.value}:
            _enter_stage(analysis, AnalysisStatus.SCRAPING, stage_hook)
            crawl = crawl_site(analysis.website.url, client=request_client, resolver=resolver)
            analysis.pages_scanned_count = len(crawl.pages)
            analysis.last_completed_stage = AnalysisStatus.SCRAPING.value
            analysis.error_message = f"Analysis completed with {len(crawl.failed_urls)} page request failure(s)." if crawl.failed_urls else None
            db.session.commit()

            _enter_stage(analysis, AnalysisStatus.ANALYZING, stage_hook)
            results = extract_keywords([page.text for page in crawl.pages])
            if not results:
                raise CrawlError("Trellis could not identify meaningful keywords on this website.")
            analysis.keywords.clear()
            db.session.flush()
            for result in results:
                analysis.keywords.append(Keyword(phrase=result.phrase, frequency=result.frequency, tfidf_score=Decimal(str(round(result.tfidf_score, 6)))))
            persist_technical_findings(
                analysis,
                run_technical_audit(
                    crawl,
                    analysis.website.url,
                    client=request_client,
                    pagespeed_api_key=pagespeed_api_key,
                ),
            )
            analysis.last_completed_stage = AnalysisStatus.ANALYZING.value
            db.session.commit()

        if analysis.last_completed_stage != AnalysisStatus.GENERATING.value:
            _enter_stage(analysis, AnalysisStatus.GENERATING, stage_hook)
            if recommendation_generator:
                recommendation_generator(analysis)
            persist_health_score(analysis)
            analysis.last_completed_stage = AnalysisStatus.GENERATING.value
            db.session.commit()

        analysis.status = AnalysisStatus.COMPLETED
        analysis.completed_at = utc_now()
        db.session.commit()
        if stage_hook:
            stage_hook(AnalysisStatus.COMPLETED, analysis)
        return analysis
    except Exception as error:
        db.session.rollback()
        saved = db.session.get(AnalysisRun, analysis.id)
        assert saved is not None
        saved.status = AnalysisStatus.FAILED
        saved.completed_at = utc_now()
        saved.error_message = str(error)[:2000]
        db.session.commit()
        if stage_hook:
            stage_hook(AnalysisStatus.FAILED, saved)
        return saved
    finally:
        if owns_client:
            request_client.close()

def run_scrape_and_keyword_analysis(website: Website, *, client: httpx.Client | None = None, resolver=socket.getaddrinfo) -> AnalysisRun:
    """Backward-compatible MVP-005 entry point."""
    return execute_analysis_run(create_analysis_run(website), client=client, resolver=resolver)
