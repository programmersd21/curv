.PHONY: install dev lint format test clean

# Install the package in editable mode
install:
	pip install -e .

# Install the package with development dependencies
dev:
	pip install -e .[dev]

# Run linters and type checkers
lint:
	ruff check .
	mypy .

# Format the code
format:
	ruff check --fix --unsafe-fixes .
	ruff format .

# Run tests with coverage
test:
	pytest

# Clean generated cache and build files
clean:
	@echo "cleaning caches..."
	@rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage
	@rm -rf src/*.egg-info dist build
	@find . -type d -name __pycache__ -exec rm -rf {} +
	