"""Runtime context shared by entry scripts, flows and modules."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AppContext:
    """Resolved project runtime context."""

    project_root: Path
    entry_file: Path
    config: dict[str, Any]

    @property
    def app_config(self) -> dict[str, Any]:
        app_config = self.config.get("app", {})
        if not isinstance(app_config, dict):
            raise ValueError("config.app must be a mapping")
        return app_config

    def flow_config(self, flow_name: str) -> dict[str, Any]:
        flows = self.config.get("flows", {})
        if not isinstance(flows, dict):
            raise ValueError("config.flows must be a mapping")
        flow_config = flows.get(flow_name, {})
        if not isinstance(flow_config, dict):
            raise ValueError(f"config.flows.{flow_name} must be a mapping")
        return flow_config
