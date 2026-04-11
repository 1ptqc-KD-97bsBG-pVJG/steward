from __future__ import annotations

import argparse

from steward.config import load_config
from steward.db.migration import upgrade_database


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Steward database management commands.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    upgrade_parser = subparsers.add_parser("upgrade", help="Apply database migrations.")
    upgrade_parser.add_argument(
        "--revision",
        default="head",
        help="Alembic revision target to upgrade to.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config = load_config()

    if args.command == "upgrade":
        upgrade_database(config.database.url, revision=args.revision)


if __name__ == "__main__":
    main()
