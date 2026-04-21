#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <old-sensitive-value> <replacement-value>" >&2
  exit 2
fi

if ! command -v git-filter-repo >/dev/null 2>&1; then
  echo "git-filter-repo is required. Install it first, then rerun this command." >&2
  exit 2
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
replace_file="$(mktemp)"
trap 'rm -f "$replace_file"' EXIT

printf 'literal:%s==>%s\n' "$1" "$2" > "$replace_file"
git -C "$repo_root" filter-repo --force --replace-text "$replace_file"
