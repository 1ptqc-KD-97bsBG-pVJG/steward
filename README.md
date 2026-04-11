# Steward

Steward is a local inference queue manager and scheduler for a home-hosted LLM setup.

## Current status

This repository currently contains the first project scaffold:

- FastAPI application factory
- minimal health check endpoint
- Python packaging and tooling config
- initial test coverage

## Local development

### Prerequisites

- Python 3.12+
- `uv`

### Install dependencies

```bash
uv sync --dev
```

### Run the API

```bash
uv run uvicorn steward.app:create_app --factory --reload
```

The API will be available at `http://127.0.0.1:8000`.

### Run tests

```bash
uv run pytest
```

