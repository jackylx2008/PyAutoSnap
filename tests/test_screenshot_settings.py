from __future__ import annotations

import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
