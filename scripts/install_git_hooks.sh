#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
git -C "$repo_root" config core.hooksPath "$repo_root/.githooks"
echo "Installed repo-managed git hooks from $repo_root/.githooks"
