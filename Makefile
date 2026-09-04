.PHONY: test test-backend test-frontend test-e2e

test: test-backend test-frontend test-e2e

test-backend:
	cd backend && .venv/bin/python -m pytest

test-frontend:
	npm --prefix frontend test

test-e2e:
	npm --prefix frontend run test:e2e
