from __future__ import annotations

import argparse
import asyncio
import json
from collections.abc import Sequence

from steward.config import load_config
from steward.db.migration import upgrade_database
from steward.db.session import create_session_factory
from steward.services.auth import bootstrap_user, issue_api_key


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Steward database management commands.")
    parser.add_argument(
        "--config",
        help="Path to the Steward config file. Defaults to STEWARD_CONFIG or ./config.yml.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    upgrade_parser = subparsers.add_parser("upgrade", help="Apply database migrations.")
    upgrade_parser.add_argument(
        "--revision",
        default="head",
        help="Alembic revision target to upgrade to.",
    )

    create_user_parser = subparsers.add_parser("create-user", help="Create a local Steward user.")
    create_user_parser.add_argument("user_id", help="Stable user identifier.")
    create_user_parser.add_argument("--alias", help="Optional human-friendly display name.")
    create_user_parser.add_argument("--admin", action="store_true", help="Grant admin privileges.")
    create_user_parser.add_argument("--owner", action="store_true", help="Mark the user as owner.")

    issue_key_parser = subparsers.add_parser("issue-key", help="Create a new API key for a user.")
    issue_key_parser.add_argument("user_id", help="Target user identifier.")
    issue_key_parser.add_argument("--client-id", help="Optional client identifier for attribution.")
    issue_key_parser.add_argument("--description", help="Optional human-readable description.")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = load_config(args.config)

    if args.command == "upgrade":
        upgrade_database(config.database.url, revision=args.revision)
        return

    session_factory = create_session_factory(config.database.url)

    if args.command == "create-user":
        user = asyncio.run(
            bootstrap_user(
                session_factory,
                user_id=args.user_id,
                alias=args.alias,
                is_admin=args.admin,
                is_owner=args.owner or args.user_id == config.auth.owner_user_id,
            )
        )
        print(
            json.dumps(
                {
                    "user_id": user.user_id,
                    "alias": user.alias,
                    "is_admin": user.is_admin,
                    "is_owner": user.is_owner,
                }
            )
        )
        return

    if args.command == "issue-key":
        issued = asyncio.run(
            issue_api_key(
                session_factory,
                user_id=args.user_id,
                client_id=args.client_id,
                description=args.description,
            )
        )
        print(
            json.dumps(
                {
                    "user_id": issued.user_id,
                    "client_id": issued.client_id,
                    "description": issued.description,
                    "key_prefix": issued.key_prefix,
                    "api_key": issued.key,
                }
            )
        )
        return

    parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
