from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

from steward.db.session import ensure_database_path, make_sync_url


def build_alembic_config(database_url: str) -> Config:
    config = Config()
    script_location = Path(__file__).resolve().parent / "migrations"
    config.set_main_option("script_location", str(script_location))
    config.set_main_option("sqlalchemy.url", make_sync_url(database_url))
    return config


def upgrade_database(database_url: str, revision: str = "head") -> None:
    ensure_database_path(database_url)
    alembic_config = build_alembic_config(database_url)
    command.upgrade(alembic_config, revision)
