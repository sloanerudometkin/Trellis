import json
import uuid
from copy import deepcopy
from pathlib import Path
from typing import Any

import jwt
import pytest

from config.testing import load_test_database_url
from trellis import create_app
from trellis.extensions import db


FIXTURES_DIR = Path(__file__).parent / "fixtures"
USER_ONE_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")
USER_TWO_ID = uuid.UUID("00000000-0000-4000-8000-000000000002")


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


def load_text_fixture(filename: str) -> str:
    return (FIXTURES_DIR / filename).read_text(encoding="utf-8")


@pytest.fixture
def sample_user_id() -> str:
    return str(USER_ONE_ID)


@pytest.fixture
def sample_website_url() -> str:
    return "https://example.com"


@pytest.fixture
def sample_business_context() -> str:
    return "A small nonprofit helping community gardens grow."


@pytest.fixture
def test_database_url() -> str:
    return load_test_database_url()


def fake_jwt_decoder(token: str) -> dict[str, Any]:
    users = {
        "user-one-token": {
            "sub": str(USER_ONE_ID),
            "email": "one@example.com",
            "user_metadata": {"name": "User One"},
        },
        "user-two-token": {
            "sub": str(USER_TWO_ID),
            "email": "two@example.com",
            "user_metadata": {"name": "User Two"},
        },
    }
    if token not in users:
        raise jwt.InvalidTokenError("invalid test token")
    return users[token]


def public_test_resolver(hostname: str, port: int):
    """Resolve test domains without making a real DNS/network request."""

    return [(2, 1, 6, "", ("93.184.216.34", port))]


@pytest.fixture
def app():
    class RuntimeTestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite+pysqlite:///:memory:"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        JWT_DECODER = staticmethod(fake_jwt_decoder)
        RATELIMIT_ENABLED = False
        ALLOW_EXTERNAL_REQUESTS = False
        URL_RESOLVER = staticmethod(public_test_resolver)

    test_app = create_app(RuntimeTestConfig)
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user_one_headers() -> dict[str, str]:
    return {"Authorization": "Bearer user-one-token"}


@pytest.fixture
def user_two_headers() -> dict[str, str]:
    return {"Authorization": "Bearer user-two-token"}


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
