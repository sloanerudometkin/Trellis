import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from config.testing import load_test_database_url


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class FakeExternalResponse:
    """Small stand-in for the part of an HTTP response our tests will use."""

    def __init__(
        self,
        *,
        json_data: dict[str, Any],
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.headers = headers or {}
        self._json_data = deepcopy(json_data)

    def json(self) -> dict[str, Any]:
        return deepcopy(self._json_data)


def load_json_fixture(filename: str) -> dict[str, Any]:
    """Load one local JSON response fixture by filename."""

    with (FIXTURES_DIR / filename).open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


@pytest.fixture
def sample_user_id() -> str:
    return "00000000-0000-4000-8000-000000000001"


@pytest.fixture
def sample_website_url() -> str:
    return "https://example.com"


@pytest.fixture
def sample_business_context() -> str:
    return "A small nonprofit helping community gardens grow."


@pytest.fixture
def test_database_url() -> str:
    return load_test_database_url()


@pytest.fixture
def scraped_homepage_html() -> str:
    return (FIXTURES_DIR / "scraped_homepage.html").read_text(encoding="utf-8")


@pytest.fixture
def pagespeed_success_response() -> FakeExternalResponse:
    return FakeExternalResponse(json_data=load_json_fixture("pagespeed_success.json"))


@pytest.fixture
def llm_recommendations_response() -> FakeExternalResponse:
    return FakeExternalResponse(
        json_data=load_json_fixture("llm_recommendations_success.json")
    )


@pytest.fixture
def llm_rate_limit_response() -> FakeExternalResponse:
    return FakeExternalResponse(
        json_data=load_json_fixture("llm_rate_limit_error.json"),
        status_code=429,
        headers={"retry-after": "60"},
    )
