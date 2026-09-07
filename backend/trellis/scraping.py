"""Small, bounded website crawler used by the MVP analysis pipeline."""

from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

from trellis.url_safety import Resolver, validate_public_url


USER_AGENT = "TrellisBot/1.0 (+https://github.com/sloanerudometkin/Passion_Project_Sloane_Rudometkin)"
MAX_PAGES = 15
MAX_TOTAL_BYTES = 2_000_000
MAX_SECONDS = 30.0
MAX_RETRIES = 2


class CrawlError(RuntimeError):
    pass


class RobotsBlockedError(CrawlError):
    pass


@dataclass(frozen=True)
class ScrapedPage:
    url: str
    text: str
    html: str = ""


@dataclass
class CrawlResult:
    pages: list[ScrapedPage]
    failed_urls: list[str] = field(default_factory=list)
    from_cache: bool = False


_CACHE: dict[str, tuple[float, CrawlResult]] = {}


def clear_crawl_cache() -> None:
    _CACHE.clear()


def sanitize_html(html: str) -> BeautifulSoup:
    """Remove executable/non-content elements before reading page text."""

    soup = BeautifulSoup(html, "html.parser")
    for element in soup(["script", "style", "noscript", "template", "svg", "form", "iframe"]):
        element.decompose()
    for element in soup.select("[hidden], [aria-hidden='true']"):
        element.decompose()
    return soup


def extract_text(html: str) -> str:
    return " ".join(sanitize_html(html).get_text(" ", strip=True).split())


def extract_same_origin_links(html: str, page_url: str, origin: str) -> list[str]:
    links: list[str] = []
    for anchor in sanitize_html(html).find_all("a", href=True):
        candidate = urljoin(page_url, anchor["href"])
        parsed = urlsplit(candidate)
        candidate_origin = f"{parsed.scheme}://{parsed.netloc}"
        if candidate_origin != origin or parsed.scheme not in {"http", "https"}:
            continue
        clean = parsed._replace(fragment="").geturl()
        if clean not in links:
            links.append(clean)
    return links


def _request_with_retry(client: httpx.Client, url: str, retries: int) -> httpx.Response:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            response = client.get(url, headers={"User-Agent": USER_AGENT})
        except httpx.TransportError as error:
            last_error = error
            if attempt == retries:
                break
            continue
        if response.status_code >= 500:
            last_error = httpx.HTTPStatusError("temporary server error", request=response.request, response=response)
            if attempt == retries:
                break
            continue
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise CrawlError(f"Website returned HTTP {response.status_code}: {url}") from error
        return response
    raise CrawlError(f"Request failed after {retries + 1} attempts: {url}") from last_error


def _robots_policy(client: httpx.Client, root_url: str) -> RobotFileParser:
    parsed = urlsplit(root_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    policy = RobotFileParser(robots_url)
    try:
        response = client.get(robots_url, headers={"User-Agent": USER_AGENT})
        if response.status_code == 200:
            policy.parse(response.text.splitlines())
        else:
            policy.parse([])
    except httpx.HTTPError:
        policy.parse([])
    return policy


def crawl_site(
    root_url: str,
    *,
    client: httpx.Client,
    resolver: Resolver,
    max_pages: int = MAX_PAGES,
    max_total_bytes: int = MAX_TOTAL_BYTES,
    max_seconds: float = MAX_SECONDS,
    retries: int = MAX_RETRIES,
    cache_ttl_seconds: int = 900,
    now: Callable[[], float] = time.monotonic,
) -> CrawlResult:
    """Crawl a public site within strict same-origin resource bounds."""

    safe_root = validate_public_url(root_url, resolver=resolver)
    cached = _CACHE.get(safe_root)
    current_time = now()
    if cached and current_time - cached[0] <= cache_ttl_seconds:
        result = cached[1]
        return CrawlResult(pages=list(result.pages), failed_urls=list(result.failed_urls), from_cache=True)

    origin_parts = urlsplit(safe_root)
    origin = f"{origin_parts.scheme}://{origin_parts.netloc}"
    robots = _robots_policy(client, safe_root)
    if not robots.can_fetch(USER_AGENT, safe_root):
        raise RobotsBlockedError("This website blocks Trellis in robots.txt.")

    started = current_time
    queue = deque([safe_root])
    seen: set[str] = set()
    pages: list[ScrapedPage] = []
    failed_urls: list[str] = []
    failure_messages: list[str] = []
    total_bytes = 0

    while queue and len(pages) < min(max_pages, MAX_PAGES):
        if now() - started > min(max_seconds, MAX_SECONDS):
            break
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        if not robots.can_fetch(USER_AGENT, url):
            continue
        try:
            safe_url = validate_public_url(url, resolver=resolver)
            response = _request_with_retry(client, safe_url, retries)
            if response.is_redirect:
                redirect = urljoin(safe_url, response.headers["location"])
                validate_public_url(redirect, resolver=resolver)
                redirect_parts = urlsplit(redirect)
                if f"{redirect_parts.scheme}://{redirect_parts.netloc}" != origin:
                    raise CrawlError("Trellis does not follow redirects outside the submitted website.")
                queue.appendleft(redirect)
                continue
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type:
                continue
            body_size = len(response.content)
            if total_bytes + body_size > min(max_total_bytes, MAX_TOTAL_BYTES):
                break
            total_bytes += body_size
            text = extract_text(response.text)
            if text:
                pages.append(ScrapedPage(url=safe_url, text=text, html=response.text))
            for link in extract_same_origin_links(response.text, safe_url, origin):
                if link not in seen and link not in queue:
                    queue.append(link)
        except (CrawlError, httpx.HTTPError, ValueError) as error:
            failed_urls.append(url)
            failure_messages.append(str(error))

    if not pages:
        if failure_messages:
            raise CrawlError(failure_messages[0])
        raise CrawlError("Trellis could not extract readable content from this website.")
    result = CrawlResult(pages=pages, failed_urls=failed_urls)
    _CACHE[safe_root] = (current_time, result)
    return result
