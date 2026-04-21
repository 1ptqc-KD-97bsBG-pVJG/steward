#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$repo_root/scripts/scan_secrets.py" --mode repo

cd "$repo_root"
UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/steward-uv-cache}" uv run --extra dev pytest tests/test_repo_hygiene.py
