.PHONY: db-upgrade dev-backend dev-frontend test test-backend test-frontend test-e2e

db-upgrade:
	cd backend && .venv/bin/alembic upgrade head

dev-backend:
	cd backend && .venv/bin/flask --app run:app run --debug

dev-frontend:
	npm --prefix frontend run dev

test: test-backend test-frontend test-e2e

test-backend:
	cd backend && .venv/bin/python -m pytest

test-frontend:
	npm --prefix frontend test

test-e2e:
	npm --prefix frontend run test:e2e
