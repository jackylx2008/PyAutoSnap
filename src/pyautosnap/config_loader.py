"""Project configuration loading utilities."""

from __future__ import annotations

import os
import platform
import re
from pathlib import Path
from typing import Any

import yaml


ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")


def load_common_env(env_file: Path) -> None:
    """Load simple KEY=VALUE pairs from common.env without overriding process env."""
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_config(config_file: Path, env_file: Path | None = None) -> dict[str, Any]:
    """Load YAML config and expand supported environment placeholders."""
    if env_file is not None:
        load_common_env(env_file)

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    raw_config = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
    if not isinstance(raw_config, dict):
        raise ValueError(f"Config root must be a mapping: {config_file}")
    return _expand_value(raw_config)


def resolve_path_value(value: str | os.PathLike[str], base_dir: Path | None = None) -> Path:
    """Resolve project path markers, env values and user home markers."""
    raw_path = os.fspath(value)
    resolved = _expand_string(raw_path)
    path = Path(resolved).expanduser()
    if not path.is_absolute() and base_dir is not None:
        path = base_dir / path
    return path


def get_cloudstation_root() -> str:
    """Return the CloudStation root selected for the current platform."""
    explicit_root = os.getenv("CLOUDSTATION_ROOT")
    if explicit_root:
        return str(Path(explicit_root).expanduser())

    system = platform.system().lower()
    env_names = {
        "windows": ("CLOUDSTATION_ROOT_WINDOWS",),
        "darwin": ("CLOUDSTATION_ROOT_MACOS", "CLOUDSTATION_ROOT_DARWIN"),
        "linux": ("CLOUDSTATION_ROOT_LINUX",),
    }.get(system, ())

    for env_name in env_names:
        env_value = os.getenv(env_name)
        if env_value:
            return str(Path(env_value).expanduser())

    return str(Path("~/CloudStation").expanduser())


def _expand_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _expand_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_expand_value(item) for item in value]
    if isinstance(value, str):
        return _expand_string(value)
    return value


def _expand_string(value: str) -> str:
    if "${CLOUDSTATION_ROOT}" in value:
        value = value.replace("${CLOUDSTATION_ROOT}", get_cloudstation_root())
    return ENV_PATTERN.sub(_replace_env_match, value)


def _replace_env_match(match: re.Match[str]) -> str:
    env_name = match.group(1)
    default = match.group(2)
    env_value = os.getenv(env_name)
    if env_value is not None:
        return env_value
    if default is not None:
        return default
    return match.group(0)
