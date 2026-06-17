.PHONY: install dev test lint format build clean

install:
	pip install .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=turbowifi

lint:
	ruff check src/ tests/
	mypy src/turbowifi/

format:
	ruff format src/ tests/

build:
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info src/*.egg-info
