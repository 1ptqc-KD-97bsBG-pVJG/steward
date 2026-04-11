from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from steward.config import load_config


def test_load_config_uses_defaults_when_file_is_missing(tmp_path: Path) -> None:
    config = load_config(tmp_path / "missing.yml")

    assert config.config_version == 1
    assert config.server.host == "127.0.0.1"
    assert config.server.port == 8000
    assert str(config.upstream.base_url) == "http://127.0.0.1:1234/v1"
    assert config.models.allowed == ["qwen/qwen3-coder-next"]


def test_load_config_reads_yaml_file(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        "\n".join(
            [
                "config_version: 1",
                "server:",
                '  host: "127.0.0.1"',
                "  port: 8100",
                '  public_base_url: "https://steward.example.ts.net"',
                "models:",
                "  allowed:",
                '    - "zai-org/glm-4.7-flash"',
            ]
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.server.port == 8100
    assert str(config.server.public_base_url) == "https://steward.example.ts.net/"
    assert config.models.allowed == ["zai-org/glm-4.7-flash"]


def test_load_config_applies_environment_overrides(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        "\n".join(
            [
                "config_version: 1",
                "queue:",
                "  max_length: 32",
                "models:",
                "  allowed:",
                '    - "qwen/qwen3-coder-next"',
            ]
        ),
        encoding="utf-8",
    )

    config = load_config(
        config_path,
        environ={
            "STEWARD_SERVER__PORT": "9000",
            "STEWARD_QUEUE__MAX_LENGTH": "128",
            'STEWARD_MODELS__ALLOWED': '["qwen/qwen3-coder-next", "zai-org/glm-4.7-flash"]',
        },
    )

    assert config.server.port == 9000
    assert config.queue.max_length == 128
    assert config.models.allowed == ["qwen/qwen3-coder-next", "zai-org/glm-4.7-flash"]


def test_load_config_rejects_invalid_version(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        "\n".join(
            [
                "config_version: 2",
                "models:",
                "  allowed:",
                '    - "qwen/qwen3-coder-next"',
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_config(config_path)


def test_load_config_rejects_empty_allowed_models(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        "\n".join(
            [
                "config_version: 1",
                "models:",
                "  allowed: []",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_config(config_path)
