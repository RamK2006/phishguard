.PHONY: dev test lint build migrate train clean

# ─── Development ───
dev:
	docker-compose up --build

dev-detached:
	docker-compose up --build -d

stop:
	docker-compose down

# ─── Database ───
migrate:
	docker-compose exec backend alembic upgrade head

migration:
	docker-compose exec backend alembic revision --autogenerate -m "$(msg)"

# ─── ML Training ───
train:
	docker-compose exec backend python -m app.ml.train

# ─── Testing ───
test:
	docker-compose exec backend pytest --cov=app --cov-fail-under=85 -v

test-frontend:
	cd dashboard && npm test

# ─── Linting ───
lint:
	docker-compose exec backend ruff check app/
	docker-compose exec backend mypy app/
	cd dashboard && npx eslint . && npx tsc --noEmit

# ─── Build ───
build:
	docker-compose build --no-cache

# ─── Clean ───
clean:
	docker-compose down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
