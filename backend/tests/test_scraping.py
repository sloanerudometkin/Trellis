import httpx
import pytest

from conftest import load_text_fixture
from trellis.scraping import (
    MAX_PAGES,
    USER_AGENT,
    CrawlError,
    RobotsBlockedError,
    clear_crawl_cache,
    crawl_site,
    extract_same_origin_links,
    extract_text,
)


def public_resolver(_hostname: str, port: int):
    return [(2, 1, 6, "", ("93.184.216.34", port))]


@pytest.fixture(autouse=True)
def empty_cache():
    clear_crawl_cache()


def client_for(handler):
    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=False)


def test_html_sanitization_and_malformed_text_extraction() -> None:
    normal = extract_text(load_text_fixture("normal_page.html"))
    malformed = extract_text(load_text_fixture("malformed_page.html"))
    empty = extract_text(load_text_fixture("empty_page.html"))

    assert "Community gardening workshops" in normal
    assert "alert" not in normal
    assert "Seed library" in malformed and "sustainable planting" in malformed
    assert empty == ""


def test_only_same_origin_links_are_discovered() -> None:
    links = extract_same_origin_links(
        load_text_fixture("normal_page.html"),
        "https://example.com/",
        "https://example.com",
    )
    assert links == ["https://example.com/programs"]


def test_robots_block_prevents_page_request() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request):
        requests.append(request)
        return httpx.Response(200, text=load_text_fixture("robots_block.txt"), request=request)

    with client_for(handler) as client, pytest.raises(RobotsBlockedError):
        crawl_site("https://example.com", client=client, resolver=public_resolver)
    assert [request.url.path for request in requests] == ["/robots.txt"]
    assert requests[0].headers["user-agent"] == USER_AGENT


def test_page_limit_is_never_allowed_above_global_cap() -> None:
    def handler(request: httpx.Request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=load_text_fixture("robots_allow.txt"), request=request)
        page_number = 0 if request.url.path == "/" else int(request.url.path.removeprefix("/page"))
        links = "".join(f'<a href="/page{number}">Page</a>' for number in range(1, 30))
        return httpx.Response(200, text=f"<main>Unique page {page_number} gardening content</main>{links}", headers={"content-type": "text/html"}, request=request)

    with client_for(handler) as client:
        result = crawl_site("https://example.com", client=client, resolver=public_resolver, max_pages=999)
    assert len(result.pages) == MAX_PAGES


def test_retry_then_success_and_cache_reuse() -> None:
    homepage_attempts = 0

    def handler(request: httpx.Request):
        nonlocal homepage_attempts
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=load_text_fixture("robots_allow.txt"), request=request)
        if request.url.path == "/":
            homepage_attempts += 1
        if request.url.path == "/" and homepage_attempts == 1:
            raise httpx.ReadTimeout("slow", request=request)
        return httpx.Response(200, text=load_text_fixture("normal_page.html"), headers={"content-type": "text/html"}, request=request)

    with client_for(handler) as client:
        first = crawl_site("https://example.com", client=client, resolver=public_resolver)
        second = crawl_site("https://example.com", client=client, resolver=public_resolver)
    assert homepage_attempts == 2
    assert len(first.pages) == 2
    assert second.from_cache is True


def test_empty_site_has_useful_failure() -> None:
    def handler(request: httpx.Request):
        body = load_text_fixture("robots_allow.txt") if request.url.path == "/robots.txt" else load_text_fixture("empty_page.html")
        return httpx.Response(200, text=body, headers={"content-type": "text/html"}, request=request)

    with client_for(handler) as client, pytest.raises(CrawlError, match="readable content"):
        crawl_site("https://example.com", client=client, resolver=public_resolver)
