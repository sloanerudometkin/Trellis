from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from test_models import EXPECTED_TABLES


def test_migration_builds_schema_on_empty_database(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "trellis_migration_test.db"
    database_url = f"sqlite+pysqlite:///{database_path}"
    monkeypatch.setenv("TEST_DATABASE_URL", database_url)

    alembic_config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    command.upgrade(alembic_config, "head")

    engine = create_engine(database_url)
    assert set(inspect(engine).get_table_names()) == EXPECTED_TABLES | {"alembic_version"}
    engine.dispose()


def test_postgres_migration_defines_rls_for_every_owned_table() -> None:
    migration = next((Path(__file__).parents[1] / "migrations" / "versions").glob("*.py"))
    source = migration.read_text(encoding="utf-8")

    for table_name in EXPECTED_TABLES:
        assert f'"{table_name}":' in source
    assert "ENABLE ROW LEVEL SECURITY" in source
    assert "auth.uid()" in source
    assert "TO authenticated" in source
