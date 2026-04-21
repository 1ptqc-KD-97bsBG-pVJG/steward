from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from steward.app import create_app
from steward.config import StewardConfig
from steward.db.cli import main as db_cli_main
from steward.db.migration import upgrade_database
from steward.db.session import create_session_factory
from steward.services.auth import issue_api_key, revoke_api_key


def test_whoami_returns_request_identity(tmp_path: Path) -> None:
    config = build_test_config(tmp_path)
    upgrade_database(config.database.url)
    raw_key = asyncio.run(seed_identity(config))

    client = TestClient(create_app(config))
    response = client.get(
        "/v1/whoami",
        headers={
            "Authorization": f"Bearer {raw_key}",
            "X-Request-Id": "req-auth-1",
        },
    )

    assert response.status_code == 200
    assert response.headers["X-Request-Id"] == "req-auth-1"
    assert response.json() == {
        "request_id": "req-auth-1",
        "user_id": "owner",
        "alias": "Owner",
        "client_id": "openclaw-wsl",
        "api_key_id": 1,
        "key_prefix": raw_key.split(".")[1],
        "is_admin": True,
        "is_owner": True,
    }


def test_whoami_rejects_unknown_key(tmp_path: Path) -> None:
    config = build_test_config(tmp_path)
    upgrade_database(config.database.url)

    client = TestClient(create_app(config))
    response = client.get("/v1/whoami", headers={"Authorization": "Bearer stwd.bad.secret"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key."}


def test_whoami_rejects_revoked_key(tmp_path: Path) -> None:
    config = build_test_config(tmp_path)
    upgrade_database(config.database.url)
    raw_key = asyncio.run(seed_identity(config))
    asyncio.run(revoke_seeded_key(config, raw_key))

    client = TestClient(create_app(config))
    response = client.get("/v1/whoami", headers={"Authorization": f"Bearer {raw_key}"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key."}


def test_db_cli_can_create_user_and_issue_key(tmp_path: Path, capsys) -> None:
    config_path = write_test_config(tmp_path)

    db_cli_main(
        [
            "--config",
            str(config_path),
            "upgrade",
        ]
    )
    db_cli_main(
        [
            "--config",
            str(config_path),
            "create-user",
            "owner",
            "--alias",
            "Owner",
            "--admin",
            "--owner",
        ]
    )
    create_output = json.loads(capsys.readouterr().out)

    assert create_output == {
        "user_id": "owner",
        "alias": "Owner",
        "is_admin": True,
        "is_owner": True,
    }

    db_cli_main(
        [
            "--config",
            str(config_path),
            "issue-key",
            "owner",
            "--client-id",
            "openclaw-wsl",
            "--description",
            "OpenClaw WSL",
        ]
    )
    issue_output = json.loads(capsys.readouterr().out)

    assert issue_output["user_id"] == "owner"
    assert issue_output["client_id"] == "openclaw-wsl"
    assert issue_output["description"] == "OpenClaw WSL"
    assert issue_output["key_prefix"]
    assert issue_output["api_key"].startswith("stwd.")


def build_test_config(tmp_path: Path) -> StewardConfig:
    return StewardConfig.model_validate(
        {
            "config_version": 1,
            "database": {"url": f"sqlite+aiosqlite:///{tmp_path / 'steward.db'}"},
            "models": {"allowed": ["qwen/qwen3-coder-next"]},
        }
    )


async def seed_identity(config: StewardConfig) -> str:
    session_factory = create_session_factory(config.database.url)
    from steward.services.auth import bootstrap_user

    await bootstrap_user(
        session_factory,
        user_id="owner",
        alias="Owner",
        is_admin=True,
        is_owner=True,
    )
    issued = await issue_api_key(
        session_factory,
        user_id="owner",
        client_id="openclaw-wsl",
        description="OpenClaw WSL",
    )
    return issued.key


async def revoke_seeded_key(config: StewardConfig, raw_key: str) -> None:
    session_factory = create_session_factory(config.database.url)
    await revoke_api_key(session_factory, key_prefix=raw_key.split(".")[1])


def write_test_config(tmp_path: Path) -> Path:
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        "\n".join(
            [
                "config_version: 1",
                "database:",
                f'  url: "sqlite+aiosqlite:///{tmp_path / "cli.db"}"',
                "models:",
                '  allowed: ["qwen/qwen3-coder-next"]',
            ]
        ),
        encoding="utf-8",
    )
    return config_path
