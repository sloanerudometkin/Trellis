import json
from types import SimpleNamespace

from trellis import auth


def test_verified_claims_are_applied_to_postgres_rls(monkeypatch) -> None:
    executed = []
    fake_db = SimpleNamespace(
        engine=SimpleNamespace(dialect=SimpleNamespace(name="postgresql")),
        session=SimpleNamespace(execute=lambda statement, parameters=None: executed.append((str(statement), parameters))),
    )
    monkeypatch.setattr(auth, "db", fake_db)
    claims = {"sub": "00000000-0000-4000-8000-000000000001", "role": "authenticated"}

    auth.apply_postgres_rls_context(claims)

    assert executed[0][0] == "SELECT set_config('request.jwt.claims', :claims, true)"
    assert json.loads(executed[0][1]["claims"])["sub"] == claims["sub"]
    assert executed[1][0] == "SET LOCAL ROLE authenticated"


def test_sqlite_tests_do_not_attempt_postgres_role_switch(monkeypatch) -> None:
    executed = []
    fake_db = SimpleNamespace(
        engine=SimpleNamespace(dialect=SimpleNamespace(name="sqlite")),
        session=SimpleNamespace(execute=lambda *args: executed.append(args)),
    )
    monkeypatch.setattr(auth, "db", fake_db)

    auth.apply_postgres_rls_context({"sub": "test-user"})

    assert executed == []
