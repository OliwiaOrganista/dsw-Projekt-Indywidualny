.PHONY: help build up down logs test lint clean deploy docs

help:
	@echo "Cloud File Ingestor - Make Commands"
	@echo "==================================="
	@echo "make build        - Build Docker images"
	@echo "make up           - Start services"
	@echo "make down         - Stop services"
	@echo "make logs         - View logs"
	@echo "make test         - Run tests"
	@echo "make lint         - Run linting"
	@echo "make clean        - Clean up containers & volumes"
	@echo "make docs         - Open API docs"
	@echo "make shell        - Start Python shell"
	@echo "make migrate      - Run database migrations"
	@echo "make deploy       - Deploy to DigitalOcean"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✅ Services started"
	@echo "API: http://localhost:8000"
	@echo "MinIO: http://localhost:9001"

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	@echo "Running tests..."
	docker-compose exec -T api pytest tests/ -v

lint:
	@echo "Linting code..."
	docker-compose exec -T api flake8 app/ worker/ --count --select=E9,F63,F7,F82 --show-source

clean:
	docker-compose down -v
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "✅ Cleaned up"

docs:
	@echo "Opening API docs at http://localhost:8000/docs"
	@command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:8000/docs || open http://localhost:8000/docs || start http://localhost:8000/docs

shell:
	docker-compose exec api python

status:
	docker-compose ps

restart:
	docker-compose restart

logs-api:
	docker-compose logs -f api

logs-worker:
	docker-compose logs -f worker

logs-db:
	docker-compose logs -f db
