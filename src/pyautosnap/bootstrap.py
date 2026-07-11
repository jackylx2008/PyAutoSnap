"""Entry bootstrap helpers."""

from __future__ import annotations

from pathlib import Path

from logging_config import setup_logger

from pyautosnap.config_loader import load_config
from pyautosnap.context import AppContext


def bootstrap_context(entry_file: str | Path, config_file: str | Path = "config.yaml") -> AppContext:
    """Load config, initialize logging and return the shared app context."""
    entry_path = Path(entry_file).resolve()
    project_root = entry_path.parent
    config_path = project_root / config_file
    env_path = project_root / "common.env"
    config = load_config(config_path, env_path)

    app_config = config.get("app", {})
    log_level = app_config.get("log_level", "INFO") if isinstance(app_config, dict) else "INFO"
    setup_logger(log_level=log_level)

    return AppContext(project_root=project_root, entry_file=entry_path, config=config)
