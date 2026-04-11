from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
import os
from typing import Any

import yaml

from steward.config.models import StewardConfig

ENV_PREFIX = "STEWARD_"
CONFIG_PATH_ENV = f"{ENV_PREFIX}CONFIG"


def load_config(
    config_path: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> StewardConfig:
    """Load configuration from YAML and environment overrides."""
    env = dict(os.environ if environ is None else environ)
    resolved_path = Path(config_path or env.get(CONFIG_PATH_ENV, "config.yml"))

    data: dict[str, Any] = {}
    if resolved_path.exists():
        data = _read_yaml(resolved_path)

    overrides = _extract_env_overrides(env)
    merged = _deep_merge(data, overrides)
    return StewardConfig.model_validate(merged)


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Config file must contain a mapping: {path}")
    return loaded


def _extract_env_overrides(environ: Mapping[str, str]) -> dict[str, Any]:
    overrides: dict[str, Any] = {}

    for key, raw_value in environ.items():
        if not key.startswith(ENV_PREFIX) or key == CONFIG_PATH_ENV:
            continue

        path = key.removeprefix(ENV_PREFIX).lower().split("__")
        value = yaml.safe_load(raw_value)

        cursor = overrides
        for segment in path[:-1]:
            cursor = cursor.setdefault(segment, {})
        cursor[path[-1]] = value

    return overrides


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)

    for key, value in override.items():
        current = merged.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            merged[key] = _deep_merge(current, value)
        else:
            merged[key] = value

    return merged
