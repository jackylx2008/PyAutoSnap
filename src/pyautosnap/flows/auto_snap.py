"""Timed screenshot flow."""

from __future__ import annotations

import time
from typing import Any

from logging_config import get_logger

from pyautosnap.context import AppContext
from pyautosnap.modules.screenshot import ScreenshotResult, capture_screenshot, settings_from_config
from pyautosnap.modules.visual_feedback import flash_capture_region

logger = get_logger(__name__)


def run(context: AppContext) -> list[ScreenshotResult]:
    """Run the timed screenshot workflow."""
    flow_config = context.flow_config("auto_snap")
    settings = settings_from_config(context.project_root, context.app_config, flow_config)
    interval_seconds = _positive_float(flow_config.get("interval_seconds", 60), "interval_seconds")
    capture_count = _non_negative_int(flow_config.get("capture_count", 0), "capture_count")
    flash_after_capture = _to_bool(flow_config.get("flash_after_capture", False))
    flash_cycles = _non_negative_int(flow_config.get("flash_cycles", 2), "flash_cycles")
    flash_duration_ms = _positive_int(flow_config.get("flash_duration_ms", 160), "flash_duration_ms")
    flash_border_width = _positive_int(flow_config.get("flash_border_width", 6), "flash_border_width")

    logger.info(
        "Starting auto screenshot flow: output_dir=%s interval_seconds=%s capture_count=%s",
        settings.output_dir,
        interval_seconds,
        capture_count,
    )

    results: list[ScreenshotResult] = []
    sequence = 1
    try:
        while capture_count == 0 or sequence <= capture_count:
            result = capture_screenshot(settings, sequence)
            results.append(result)
            logger.info(
                "Screenshot captured: path=%s size=%sx%s sequence=%s",
                result.path,
                result.width,
                result.height,
                result.sequence,
            )
            if flash_after_capture:
                try:
                    flash_capture_region(
                        settings.region,
                        cycles=flash_cycles,
                        duration_ms=flash_duration_ms,
                        border_width=flash_border_width,
                    )
                except Exception as exc:
                    logger.warning("Capture region flash failed: %s", exc)

            sequence += 1
            if capture_count != 0 and sequence > capture_count:
                break
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        logger.info("Auto screenshot flow stopped by user")

    logger.info("Auto screenshot flow finished: captured=%s", len(results))
    return results


def _positive_float(value: Any, field_name: str) -> float:
    number = float(value)
    if number <= 0:
        raise ValueError(f"{field_name} must be greater than 0")
    return number


def _non_negative_int(value: Any, field_name: str) -> int:
    number = int(value)
    if number < 0:
        raise ValueError(f"{field_name} must be greater than or equal to 0")
    return number


def _positive_int(value: Any, field_name: str) -> int:
    number = int(value)
    if number <= 0:
        raise ValueError(f"{field_name} must be greater than 0")
    return number


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)
