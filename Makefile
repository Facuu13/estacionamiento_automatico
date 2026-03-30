.PHONY: up down logs migrate test test-backend test-e2e

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	cd backend && alembic upgrade head

test: test-backend

test-backend:
	cd backend && .venv/bin/pytest -q

test-e2e:
	cd frontend && npx playwright test

test-all: test-backend test-e2e
