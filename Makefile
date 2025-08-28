.PHONY: help install install-dev test test-cov lint format type-check clean build run

help: ## Show this help message
	@echo "Sleeper AI Lineup Optimizer - Development Commands"
	@echo "=================================================="
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=src --cov-report=html --cov-report=term-missing

lint: ## Run linting checks
	flake8 src/ tests/
	black --check src/ tests/

format: ## Format code with Black
	black src/ tests/

type-check: ## Run type checking with MyPy
	mypy src/

check: lint type-check ## Run all code quality checks

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build executable with PyInstaller
	pyinstaller sleeper_optimizer.spec

run: ## Run the application
	python -m src.main

dev: install-dev ## Setup development environment
	pre-commit install

ci: test lint type-check ## Run CI checks locally
