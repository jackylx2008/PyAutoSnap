from __future__ import annotations

import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch

from pyautosnap.modules.monitors import MonitorInfo
from pyautosnap.modules.screenshot import settings_from_config


class ScreenshotSettingsTest(unittest.TestCase):
    def test_settings_from_config_resolves_output_dir(self) -> None:
        with TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            settings = settings_from_config(
                tmp_path,
                {"output_dir": "output/screenshots"},
                {"image_format": "png"},
            )

            self.assertEqual(settings.output_dir, tmp_path / "output" / "screenshots")
            self.assertEqual(settings.image_format, "png")

    def test_settings_from_config_rejects_unknown_format(self) -> None:
        with TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            with self.assertRaisesRegex(ValueError, "Unsupported image format"):
                settings_from_config(tmp_path, {"output_dir": "output"}, {"image_format": "gif"})

    def test_settings_from_config_translates_screen_local_region(self) -> None:
        monitor = MonitorInfo(
            index=2,
            device_name="DISPLAY2",
            left=2560,
            top=100,
            right=4480,
            bottom=1180,
            is_primary=False,
        )
        with TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            with patch("pyautosnap.modules.screenshot.get_monitor", return_value=monitor):
                settings = settings_from_config(
                    tmp_path,
                    {"output_dir": "output"},
                    {
                        "image_format": "png",
                        "region": {
                            "screen_index": 2,
                            "left": 10,
                            "top": 20,
                            "width": 300,
                            "height": 400,
                        },
                    },
                )

        self.assertEqual(settings.region, (2570, 120, 2870, 520))


if __name__ == "__main__":
    unittest.main()
