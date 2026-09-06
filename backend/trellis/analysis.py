"""MVP analysis stages that turn a saved Website into persisted keywords."""

import socket
from decimal import Decimal

import httpx

from trellis.extensions import db
from trellis.keywords import extract_keywords
from trellis.models import AnalysisRun, AnalysisStatus, Keyword, Website, utc_now
from trellis.scraping import CrawlError, crawl_site


def run_scrape_and_keyword_analysis(
    website: Website,
    *,
    client: httpx.Client | None = None,
    resolver=socket.getaddrinfo,
) -> AnalysisRun:
    """Run and persist MVP-005 atomically, retaining a useful failed run."""

    analysis = AnalysisRun(website=website, status=AnalysisStatus.SCRAPING)
    db.session.add(analysis)
    db.session.commit()
    owns_client = client is None
    request_client = client or httpx.Client(timeout=httpx.Timeout(10.0), follow_redirects=False)

    try:
        crawl = crawl_site(website.url, client=request_client, resolver=resolver)
        analysis.pages_scanned_count = len(crawl.pages)
        analysis.status = AnalysisStatus.ANALYZING
        db.session.commit()

        for result in extract_keywords([page.text for page in crawl.pages]):
            analysis.keywords.append(
                Keyword(
                    phrase=result.phrase,
                    frequency=result.frequency,
                    tfidf_score=Decimal(str(round(result.tfidf_score, 6))),
                )
            )
        if not analysis.keywords:
            raise CrawlError("Trellis could not identify meaningful keywords on this website.")
        analysis.status = AnalysisStatus.COMPLETED
        analysis.completed_at = utc_now()
        analysis.error_message = (
            f"Analysis completed with {len(crawl.failed_urls)} page request failure(s)."
            if crawl.failed_urls
            else None
        )
        db.session.commit()
        return analysis
    except Exception as error:
        db.session.rollback()
        saved_analysis = db.session.get(AnalysisRun, analysis.id)
        assert saved_analysis is not None
        saved_analysis.status = AnalysisStatus.FAILED
        saved_analysis.completed_at = utc_now()
        saved_analysis.error_message = str(error)[:2000]
        saved_analysis.keywords.clear()
        db.session.commit()
        return saved_analysis
    finally:
        if owns_client:
            request_client.close()
