import os
from urllib.parse import urlsplit

from config.application import Config


IN_MEMORY_TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"


def _normalized_database_url(database_url: str) -> str:
    return database_url.rstrip("/")


def _database_name(database_url: str) -> str:
    return urlsplit(database_url).path.rstrip("/").rsplit("/", maxsplit=1)[-1]


def load_test_database_url() -> str:
    """Return a test-only database URL after applying safety checks."""

    test_database_url = os.getenv(
        "TEST_DATABASE_URL", IN_MEMORY_TEST_DATABASE_URL
    ).strip()
    development_database_url = os.getenv("DATABASE_URL", "").strip()

    if not test_database_url:
        raise RuntimeError("TEST_DATABASE_URL cannot be empty.")

    if development_database_url and _normalized_database_url(
        test_database_url
    ) == _normalized_database_url(development_database_url):
        raise RuntimeError(
            "TEST_DATABASE_URL must not point to the development database."
        )

    if (
        test_database_url != IN_MEMORY_TEST_DATABASE_URL
        and "test" not in _database_name(test_database_url).lower()
    ):
        raise RuntimeError(
            "The test database name must contain 'test' as a safety marker."
        )

    return test_database_url


class TestConfig(Config):
    """Settings used only while running automated backend tests."""

    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOW_EXTERNAL_REQUESTS = False
    SQLALCHEMY_DATABASE_URI = load_test_database_url()
