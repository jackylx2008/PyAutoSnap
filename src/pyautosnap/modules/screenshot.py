"""Screenshot capture primitives."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from pyautosnap.config_loader import resolve_path_value


SUPPORTED_FORMATS = {"png": "PNG", "jpg": "JPEG", "jpeg": "JPEG"}


@dataclass(frozen=True)
class ScreenshotSettings:
    """Resolved screenshot capture settings."""

    output_dir: Path
    image_format: str = "png"
    filename_template: str = "snap_{timestamp}_{sequence:04d}.{extension}"
    jpeg_quality: int = 95
    region: tuple[int, int, int, int] | None = None
    all_screens: bool = True


@dataclass(frozen=True)
class ScreenshotResult:
    """Result for one captured screenshot."""

    path: Path
    captured_at: datetime
    sequence: int
    width: int
    height: int


def settings_from_config(project_root: Path, app_config: dict[str, Any], flow_config: dict[str, Any]) -> ScreenshotSettings:
    """Build screenshot settings from app and flow config mappings."""
    output_dir = resolve_path_value(app_config.get("output_dir", "output/screenshots"), project_root)
    image_format = str(flow_config.get("image_format", "png")).lower().lstrip(".")
    if image_format not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported image format: {image_format}")

    region = _parse_region(flow_config.get("region"))
    jpeg_quality = int(flow_config.get("jpeg_quality", 95))
    if not 1 <= jpeg_quality <= 100:
        raise ValueError("jpeg_quality must be between 1 and 100")

    return ScreenshotSettings(
        output_dir=output_dir,
        image_format=image_format,
        filename_template=str(flow_config.get("filename_template", "snap_{timestamp}_{sequence:04d}.{extension}")),
        jpeg_quality=jpeg_quality,
        region=region,
        all_screens=_to_bool(flow_config.get("all_screens", True)),
    )


def capture_screenshot(settings: ScreenshotSettings, sequence: int, captured_at: datetime | None = None) -> ScreenshotResult:
    """Capture one screenshot and save it to the configured output directory."""
    try:
        from PIL import ImageGrab
    except ImportError as exc:
        raise RuntimeError("Pillow is required for screenshot capture. Install dependencies from requirements.txt.") from exc

    captured_at = captured_at or datetime.now()
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    extension = "jpg" if settings.image_format == "jpeg" else settings.image_format
    output_path = _build_output_path(settings, captured_at, sequence, extension)

    image = ImageGrab.grab(bbox=settings.region, all_screens=settings.all_screens)
    save_kwargs: dict[str, Any] = {}
    if SUPPORTED_FORMATS[settings.image_format] == "JPEG":
        image = image.convert("RGB")
        save_kwargs["quality"] = settings.jpeg_quality
        save_kwargs["optimize"] = True
    image.save(output_path, format=SUPPORTED_FORMATS[settings.image_format], **save_kwargs)

    return ScreenshotResult(
        path=output_path,
        captured_at=captured_at,
        sequence=sequence,
        width=image.width,
        height=image.height,
    )


def _build_output_path(
    settings: ScreenshotSettings,
    captured_at: datetime,
    sequence: int,
    extension: str,
) -> Path:
    timestamp = captured_at.strftime("%Y%m%d_%H%M%S")
    filename = settings.filename_template.format(
        timestamp=timestamp,
        sequence=sequence,
        extension=extension,
    )
    if Path(filename).name != filename:
        raise ValueError("filename_template must produce a filename, not a path")
    return settings.output_dir / filename


def _parse_region(value: Any) -> tuple[int, int, int, int] | None:
    if value in (None, "", False):
        return None
    if not isinstance(value, dict):
        raise ValueError("region must be null or a mapping with left/top/width/height")
    left = int(value.get("left", 0))
    top = int(value.get("top", 0))
    width = int(value["width"])
    height = int(value["height"])
    if width <= 0 or height <= 0:
        raise ValueError("region width and height must be positive")
    return (left, top, left + width, top + height)


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)
