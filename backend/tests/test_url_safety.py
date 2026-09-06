import socket

import pytest

from trellis.url_safety import UnsafeUrlError, normalize_url, validate_public_url


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Example.COM", "https://example.com"),
        ("https://Example.COM:443/", "https://example.com"),
        ("http://example.com:80/about#team", "http://example.com/about"),
        ("https://example.com/path?q=one", "https://example.com/path?q=one"),
    ],
)
def test_normalize_url(raw: str, expected: str) -> None:
    assert normalize_url(raw) == expected


@pytest.mark.parametrize(
    "url",
    [
        "ftp://example.com",
        "https://user:password@example.com",
        "https://localhost",
        "https://service.local",
        "https://example.com:99999",
    ],
)
def test_normalize_url_rejects_invalid_or_internal_urls(url: str) -> None:
    with pytest.raises(UnsafeUrlError):
        normalize_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1",
        "http://10.0.0.4",
        "http://172.16.2.3",
        "http://192.168.1.2",
        "http://169.254.169.254/latest/meta-data",
        "http://[::1]",
        "http://[fc00::1]",
    ],
)
def test_validate_public_url_rejects_private_ip_literals(url: str) -> None:
    def resolver_should_not_run(_hostname: str, _port: int):
        raise AssertionError("Literal private addresses must be rejected before DNS")

    with pytest.raises(UnsafeUrlError, match="Private or internal"):
        validate_public_url(url, resolver=resolver_should_not_run)


def test_validate_public_url_rejects_hostname_resolving_to_private_address() -> None:
    def private_resolver(_hostname: str, port: int):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.7", port))]

    with pytest.raises(UnsafeUrlError, match="Private or internal"):
        validate_public_url("https://internal.example", resolver=private_resolver)


def test_validate_public_url_accepts_hostname_when_every_address_is_public() -> None:
    def public_resolver(_hostname: str, port: int):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]

    assert validate_public_url("example.com", resolver=public_resolver) == "https://example.com"
