from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_FILE_SUFFIXES = {
    ".md",
    ".mako",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
FORBIDDEN_TS_NET = re.compile(r"\b(?![A-Za-z0-9.-]*example\.ts\.net\b)[A-Za-z0-9.-]+\.ts\.net\b")
REQUIRED_GITIGNORE_PATTERNS = {
    "config.yml",
    ".env",
    ".env.*",
    "var/",
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    ".gitleaks-report*.json",
}
FORBIDDEN_TRACKED_PATHS = (
    re.compile(r"(^|/)config\.yml$"),
    re.compile(r"(^|/)\.env(\..+)?$"),
    re.compile(r"(^|/)var/"),
    re.compile(r".*\.db$"),
    re.compile(r".*\.sqlite3?$"),
)


def test_gitignore_covers_local_secret_and_state_files() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    for pattern in REQUIRED_GITIGNORE_PATTERNS:
        assert pattern in gitignore


def test_tracked_files_do_not_include_local_secret_or_state_paths() -> None:
    for relative_path in tracked_files():
        normalized = relative_path.as_posix()
        assert not any(
            pattern.search(normalized) for pattern in FORBIDDEN_TRACKED_PATHS
        ), normalized


def test_tracked_text_files_do_not_contain_real_ts_net_hostnames() -> None:
    offenders: list[str] = []

    for relative_path in tracked_files():
        if relative_path.suffix not in TEXT_FILE_SUFFIXES:
            continue

        contents = (ROOT / relative_path).read_text(encoding="utf-8")
        match = FORBIDDEN_TS_NET.search(contents)
        if match:
            offenders.append(f"{relative_path}:{match.group(0)}")

    assert offenders == []


def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    return [Path(line) for line in output.splitlines() if line.strip()]
