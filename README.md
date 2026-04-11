# Steward

Steward is a local inference queue manager and scheduler for a home-hosted LLM setup.

## Current status

This repository currently contains the first project scaffold:

- FastAPI application factory
- minimal health check endpoint
- versioned YAML config with env overrides
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

To load a specific config file:

```bash
STEWARD_CONFIG=config.example.yml uv run uvicorn steward.app:create_app --factory --reload
```

Environment overrides use `STEWARD_` keys with `__` separators for nesting. Example:

```bash
STEWARD_SERVER__PORT=9000 uv run uvicorn steward.app:create_app --factory
```

### Apply database migrations

```bash
uv run steward-db upgrade
```

To point migrations at a specific config file:

```bash
STEWARD_CONFIG=config.example.yml uv run steward-db upgrade
```

### Run tests

```bash
uv run --extra dev pytest
```
