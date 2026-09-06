"""Normalize user website URLs and prevent server-side request forgery (SSRF)."""

import ipaddress
import socket
from collections.abc import Callable, Iterable
from urllib.parse import urlsplit, urlunsplit


class UnsafeUrlError(ValueError):
    """Raised when a URL cannot safely be fetched by Trellis."""


Resolver = Callable[[str, int], Iterable[tuple]]


def _is_public_address(value: str) -> bool:
    address = ipaddress.ip_address(value)
    return address.is_global


def normalize_url(value: str) -> str:
    """Return one canonical HTTP(S) URL for validation and duplicate checks."""

    candidate = value.strip()
    if "://" not in candidate:
        candidate = f"https://{candidate}"

    try:
        parsed = urlsplit(candidate)
        port = parsed.port
    except ValueError as error:
        raise UnsafeUrlError("Enter a valid website URL.") from error

    if parsed.scheme.lower() not in {"http", "https"}:
        raise UnsafeUrlError("Only http and https website URLs are allowed.")
    if not parsed.hostname or parsed.username or parsed.password:
        raise UnsafeUrlError("Enter a valid public website URL without credentials.")

    try:
        hostname = parsed.hostname.encode("idna").decode("ascii").lower()
    except UnicodeError as error:
        raise UnsafeUrlError("Enter a valid website hostname.") from error

    if hostname == "localhost" or hostname.endswith(".localhost") or hostname.endswith(".local"):
        raise UnsafeUrlError("Private or internal website addresses are not allowed.")

    if port is not None and not 1 <= port <= 65535:
        raise UnsafeUrlError("Enter a valid website port.")

    default_port = (parsed.scheme.lower() == "http" and port == 80) or (
        parsed.scheme.lower() == "https" and port == 443
    )
    host_for_netloc = f"[{hostname}]" if ":" in hostname else hostname
    netloc = host_for_netloc if port is None or default_port else f"{host_for_netloc}:{port}"
    path = parsed.path or "/"
    if path == "/":
        path = ""

    return urlunsplit((parsed.scheme.lower(), netloc, path, parsed.query, ""))


def validate_public_url(value: str, resolver: Resolver = socket.getaddrinfo) -> str:
    """Normalize a URL and reject every resolved non-public IP address."""

    normalized = normalize_url(value)
    parsed = urlsplit(normalized)
    hostname = parsed.hostname
    assert hostname is not None

    try:
        literal = ipaddress.ip_address(hostname)
    except ValueError:
        literal = None

    if literal is not None:
        if not literal.is_global:
            raise UnsafeUrlError("Private or internal website addresses are not allowed.")
        return normalized

    try:
        answers = list(resolver(hostname, parsed.port or (443 if parsed.scheme == "https" else 80)))
    except OSError as error:
        raise UnsafeUrlError("That website hostname could not be found.") from error

    addresses = {answer[4][0] for answer in answers}
    if not addresses:
        raise UnsafeUrlError("That website hostname could not be found.")
    if any(not _is_public_address(address) for address in addresses):
        raise UnsafeUrlError("Private or internal website addresses are not allowed.")
    return normalized
