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

### Public repo safety setup

Install local git hooks once per clone:

```bash
./scripts/install_git_hooks.sh
```

Run the repo safety checks manually before pushing:

```bash
./scripts/check_safe_to_push.sh
```

The secret scan uses `gitleaks`. Install it locally before using the hooks or manual scan command.
If `gitleaks` is not installed, the scanner falls back to Docker automatically.

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

### Create a user

```bash
uv run steward-db create-user owner --alias "Owner" --admin --owner
```

### Issue an API key

```bash
uv run steward-db issue-key owner --client-id openclaw-wsl --description "OpenClaw WSL"
```

The command returns JSON that includes the one-time plaintext API key. Steward stores only a
hash plus a visible key prefix in the database.

### Run tests

```bash
uv run --extra dev pytest
```

### Secret scanning only

Scan just staged changes:

```bash
./scripts/scan_secrets.py --mode staged
```

Scan the full tracked repo:

```bash
./scripts/scan_secrets.py --mode repo
```

### Public repo hygiene rules

- Never commit `config.yml`, `.env*`, `var/`, or local database files.
- Never paste CLI-issued plaintext API keys into docs, commits, or GitHub comments.
- Use placeholder hostnames like `steward.example.ts.net`, not real tailnet or internal hostnames.
- If a real secret or internal hostname lands in git history, rotate the credential first if needed, then rewrite history before continuing.

### Rewrite published history

If you need to purge already-published sensitive text from git history, use:

```bash
./scripts/rewrite_public_history.sh "old-sensitive-value" "replacement-value"
```

This requires `git-filter-repo` to be installed locally and will rewrite commit hashes.
