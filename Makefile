ENV ?= development
ENV_FILE = .env.$(ENV)
COMPOSE = docker-compose --env-file $(ENV_FILE)

.PHONY: help build up down logs test format lint precommit generate-requirements \
        build-dev build-prod up-dev up-prod test-dev test-prod

help:
	@echo "Commands:"
	@echo "  make build ENV=development|production"
	@echo "  make up ENV=development|production"
	@echo "  make down"
	@echo "  make logs"
	@echo "  make test ENV=development|production"
	@echo "  make format"
	@echo "  make lint"
	@echo "  make precommit-install"
	@echo "  make generate-requirements"
	@echo "  make build-dev/build-prod"
	@echo "  make up-dev/up-prod"
	@echo "  make test-dev/test-prod"

build:
	$(COMPOSE) build --build-arg ENV=$(ENV)

build-dev:
	$(MAKE) build ENV=development

build-prod:
	$(MAKE) build ENV=production

up:
	$(COMPOSE) up --build

up-dev:
	$(MAKE) up ENV=development

up-prod:
	$(MAKE) up ENV=production

down:
	$(COMPOSE) down -v

logs:
	$(COMPOSE) logs -f

test:
	$(COMPOSE) run --rm web pytest

test-dev:
	$(MAKE) test ENV=development

test-prod:
	$(MAKE) test ENV=production

format:
	black app tests

lint:
	ruff . && isort --profile black .

precommit-install:
	pre-commit install

generate-requirements:
	poetry export --without-hashes --format=requirements.txt -o requirements.txt
	poetry export --without-hashes --dev --format=requirements.txt -o requirements-dev.txt
