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
    analysis_columns = {column["name"] for column in inspect(engine).get_columns("analysis_runs")}
    assert "last_completed_stage" in analysis_columns
    engine.dispose()


def test_postgres_migration_defines_rls_for_every_owned_table() -> None:
    migration_dir = Path(__file__).parents[1] / "migrations" / "versions"
    source = "\n".join(path.read_text(encoding="utf-8") for path in migration_dir.glob("*.py"))

    for table_name in EXPECTED_TABLES:
        assert f'"{table_name}":' in source
    assert "ENABLE ROW LEVEL SECURITY" in source
    assert "auth.uid()" in source
    assert "TO authenticated" in source
