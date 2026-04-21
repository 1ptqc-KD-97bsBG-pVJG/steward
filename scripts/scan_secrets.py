#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GITLEAKS_CONFIG = ROOT / "gitleaks.toml"
GITLEAKS_IMAGE = "ghcr.io/gitleaks/gitleaks:v8.30.0"


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan Steward for secrets before commit or push.")
    parser.add_argument(
        "--mode",
        choices=("staged", "repo"),
        required=True,
        help="Scan staged files or the full tracked repository.",
    )
    args = parser.parse_args()

    runner = resolve_runner()
    if runner is None:
        print(
            (
                "Neither gitleaks nor docker is installed. "
                "Install one of them before running the secret scan."
            ),
            file=sys.stderr,
        )
        return 2

    if args.mode == "staged":
        paths = tracked_staged_paths()
        if not paths:
            print("No staged tracked files to scan.")
            return 0
        with staged_snapshot(paths) as source_dir:
            return run_gitleaks(runner, source_dir)

    with tracked_repo_snapshot() as source_dir:
        return run_gitleaks(runner, source_dir)


def resolve_runner() -> tuple[str, str] | None:
    gitleaks = shutil.which("gitleaks")
    if gitleaks is not None:
        return ("binary", gitleaks)

    docker = shutil.which("docker")
    if docker is not None:
        return ("docker", docker)

    return None


def tracked_staged_paths() -> list[Path]:
    output = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=ROOT,
        text=True,
    )
    return [Path(line) for line in output.splitlines() if line.strip()]


def tracked_repo_paths() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    return [Path(line) for line in output.splitlines() if line.strip()]


class SnapshotContext:
    def __init__(self, directory: str) -> None:
        self.directory = Path(directory)

    def __enter__(self) -> Path:
        return self.directory

    def __exit__(self, exc_type, exc, tb) -> None:
        shutil.rmtree(self.directory)


def staged_snapshot(paths: list[Path]) -> SnapshotContext:
    temp_dir = tempfile.mkdtemp(prefix="steward-gitleaks-staged-")
    snapshot_dir = Path(temp_dir)

    for relative_path in paths:
        destination = snapshot_dir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        blob = subprocess.check_output(["git", "show", f":{relative_path.as_posix()}"], cwd=ROOT)
        destination.write_bytes(blob)

    return SnapshotContext(temp_dir)


def tracked_repo_snapshot() -> SnapshotContext:
    temp_dir = tempfile.mkdtemp(prefix="steward-gitleaks-repo-")
    snapshot_dir = Path(temp_dir)

    for relative_path in tracked_repo_paths():
        source = ROOT / relative_path
        if source.is_dir() or not source.exists():
            continue
        destination = snapshot_dir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())

    return SnapshotContext(temp_dir)


def run_gitleaks(runner: tuple[str, str], source_dir: Path) -> int:
    report_fd, report_name = tempfile.mkstemp(prefix="steward-gitleaks-report-", suffix=".json")
    os.close(report_fd)
    report_path = Path(report_name)
    env = os.environ.copy()
    kind, executable = runner
    command = build_command(kind, executable, source_dir, report_path)

    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
    if result.returncode == 0:
        print("Secret scan passed.")
        report_path.unlink(missing_ok=True)
        return 0

    print("Secret scan failed.", file=sys.stderr)
    print(f"Review the report at: {report_path}", file=sys.stderr)
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


def build_command(kind: str, executable: str, source_dir: Path, report_path: Path) -> list[str]:
    if kind == "binary":
        return [
            executable,
            "dir",
            str(source_dir),
            "--config",
            str(GITLEAKS_CONFIG),
            "--report-format",
            "json",
            "--report-path",
            str(report_path),
        ]

    return [
        executable,
        "run",
        "--rm",
        "-v",
        f"{source_dir}:/scan:ro",
        "-v",
        f"{GITLEAKS_CONFIG}:/config/gitleaks.toml:ro",
        "-v",
        f"{report_path.parent}:/report",
        GITLEAKS_IMAGE,
        "dir",
        "/scan",
        "--config",
        "/config/gitleaks.toml",
        "--report-format",
        "json",
        "--report-path",
        f"/report/{report_path.name}",
    ]


if __name__ == "__main__":
    raise SystemExit(main())
