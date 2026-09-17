.PHONY: help install dev-api dev-web test-api test-web lint format docker-up docker-down db-migrate

help:
	@echo "AI PlacementOS Development Commands:"
	@echo "  make install      - Install all dependencies for API and Web"
	@echo "  make dev-api      - Run FastAPI dev server on port 8000"
	@echo "  make dev-web      - Run Next.js dev server on port 3000"
	@echo "  make test-api     - Run pytest backend test suite"
	@echo "  make test-web     - Run frontend test suite"
	@echo "  make docker-up    - Start PostgreSQL, Redis, API, and Web containers"
	@echo "  make docker-down  - Stop all running containers"

install:
	cd apps/api && pip install -r requirements.txt
	cd apps/web && npm install

dev-api:
	cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-web:
	cd apps/web && npm run dev

test-api:
	cd apps/api && pytest -v --tb=short

docker-up:
	docker compose up -d

docker-down:
	docker compose down
