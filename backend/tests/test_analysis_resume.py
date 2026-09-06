from decimal import Decimal
from uuid import UUID

import httpx

from conftest import load_text_fixture
from trellis.analysis_pipeline import create_analysis_run, execute_analysis_run
from trellis.extensions import db
from trellis.models import AnalysisRun, AnalysisStatus, Keyword, User, Website
from trellis.scraping import clear_crawl_cache


def public_resolver(_hostname: str, port: int):
    return [(2, 1, 6, "", ("93.184.216.34", port))]


def setup_run() -> AnalysisRun:
    user = User(id=UUID("00000000-0000-4000-8000-000000000001"), name="Owner", email="owner@example.com")
    website = Website(user=user, url="https://example.com", business_name="Example")
    db.session.add(user)
    db.session.commit()
    clear_crawl_cache()
    return create_analysis_run(website)


def successful_client() -> httpx.Client:
    def handler(request: httpx.Request):
        body = load_text_fixture("robots_allow.txt") if request.url.path == "/robots.txt" else load_text_fixture("duplicate_page.html")
        return httpx.Response(200, text=body, headers={"content-type": "text/html"}, request=request)
    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=False)


def test_all_states_are_persisted_in_order(app) -> None:
    analysis = setup_run()
    states = [analysis.status]

    def record(status: AnalysisStatus, run: AnalysisRun) -> None:
        assert db.session.get(AnalysisRun, run.id).status == status
        states.append(status)

    with successful_client() as client:
        execute_analysis_run(analysis, client=client, resolver=public_resolver, stage_hook=record)

    assert states == [
        AnalysisStatus.QUEUED,
        AnalysisStatus.SCRAPING,
        AnalysisStatus.ANALYZING,
        AnalysisStatus.GENERATING,
        AnalysisStatus.COMPLETED,
    ]
    assert analysis.last_completed_stage == AnalysisStatus.GENERATING.value


def test_failure_is_persisted_with_last_completed_stage(app) -> None:
    analysis = setup_run()
    states: list[AnalysisStatus] = []

    def fail_during_generation(status: AnalysisStatus, _run: AnalysisRun) -> None:
        states.append(status)
        if status == AnalysisStatus.GENERATING:
            raise RuntimeError("controlled generation interruption")

    with successful_client() as client:
        execute_analysis_run(analysis, client=client, resolver=public_resolver, stage_hook=fail_during_generation)

    saved = db.session.get(AnalysisRun, analysis.id)
    assert saved.status == AnalysisStatus.FAILED
    assert saved.last_completed_stage == AnalysisStatus.ANALYZING.value
    assert saved.error_message == "controlled generation interruption"
    assert states[-1] == AnalysisStatus.FAILED


def test_retry_resumes_after_analyzing_without_scraping_or_duplicate_keywords(app) -> None:
    analysis = setup_run()
    analysis.status = AnalysisStatus.FAILED
    analysis.last_completed_stage = AnalysisStatus.ANALYZING.value
    analysis.pages_scanned_count = 3
    analysis.keywords.append(Keyword(phrase="community garden", frequency=4, tfidf_score=Decimal("0.8")))
    db.session.commit()

    class ClientThatMustNotRun:
        def get(self, *_args, **_kwargs):
            raise AssertionError("A completed scrape/analyze checkpoint must not be repeated")
        def close(self):
            pass

    resumed = execute_analysis_run(analysis, client=ClientThatMustNotRun(), resolver=public_resolver)
    assert resumed.status == AnalysisStatus.COMPLETED
    assert resumed.pages_scanned_count == 3
    assert [keyword.phrase for keyword in resumed.keywords] == ["community garden"]


def test_retry_of_completed_run_is_idempotent(app) -> None:
    analysis = setup_run()
    analysis.status = AnalysisStatus.COMPLETED
    analysis.last_completed_stage = AnalysisStatus.GENERATING.value
    analysis.keywords.append(Keyword(phrase="garden strategy", frequency=2, tfidf_score=Decimal("0.7")))
    db.session.commit()
    same_run = execute_analysis_run(analysis)
    assert same_run.id == analysis.id
    assert len(same_run.keywords) == 1


def test_resume_after_generation_checkpoint_only_marks_run_complete(app) -> None:
    analysis = setup_run()

    def interrupt_before_terminal_response(status: AnalysisStatus, _run: AnalysisRun) -> None:
        if status == AnalysisStatus.COMPLETED:
            raise RuntimeError("response interrupted after generation checkpoint")

    with successful_client() as client:
        failed = execute_analysis_run(analysis, client=client, resolver=public_resolver, stage_hook=interrupt_before_terminal_response)
    assert failed.status == AnalysisStatus.FAILED
    assert failed.last_completed_stage == AnalysisStatus.GENERATING.value
    keyword_ids = [keyword.id for keyword in failed.keywords]

    class ClientThatMustNotRun:
        def get(self, *_args, **_kwargs):
            raise AssertionError("Completed stages must not run again")
        def close(self):
            pass

    resumed = execute_analysis_run(failed, client=ClientThatMustNotRun(), resolver=public_resolver)
    assert resumed.status == AnalysisStatus.COMPLETED
    assert [keyword.id for keyword in resumed.keywords] == keyword_ids
