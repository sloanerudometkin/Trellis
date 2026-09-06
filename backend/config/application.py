import os
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]


def normalize_database_url(database_url: str) -> str:
    """Use psycopg 3 when a provider supplies a generic PostgreSQL URL."""

    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


class Config:
    SQLALCHEMY_DATABASE_URI = normalize_database_url(
        os.getenv(
            "DATABASE_URL",
            f"sqlite+pysqlite:///{BACKEND_DIR / 'trellis-dev.db'}",
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_JWT_AUDIENCE = os.getenv("SUPABASE_JWT_AUDIENCE", "authenticated")
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    JWT_DECODER = None
    ALLOW_EXTERNAL_REQUESTS = True
    RATELIMIT_STORAGE_URI = "memory://"
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


class DevelopmentConfig(Config):
    DEBUG = True
