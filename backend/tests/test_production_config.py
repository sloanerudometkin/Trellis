from config.application import normalize_database_url
from trellis import create_app


def test_production_config_disables_debugging(monkeypatch) -> None:
    monkeypatch.setenv("FLASK_ENV", "production")
    app = create_app()
    assert app.config["DEBUG"] is False
    assert app.config["TESTING"] is False


def test_production_database_url_uses_psycopg() -> None:
    assert normalize_database_url("postgresql://user:secret@db.example/trellis").startswith("postgresql+psycopg://")
