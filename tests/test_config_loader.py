from __future__ import annotations

import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch

from pyautosnap.config_loader import load_config, resolve_path_value


class ConfigLoaderTest(unittest.TestCase):
    def test_load_config_expands_env_default(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with TemporaryDirectory() as temp_dir:
                tmp_path = Path(temp_dir)
                config_file = tmp_path / "config.yaml"
                config_file.write_text("app:\n  log_level: ${LOG_LEVEL:-INFO}\n", encoding="utf-8")

                config = load_config(config_file)

        self.assertEqual(config["app"]["log_level"], "INFO")

    def test_load_config_reads_common_env(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with TemporaryDirectory() as temp_dir:
                tmp_path = Path(temp_dir)
                config_file = tmp_path / "config.yaml"
                env_file = tmp_path / "common.env"
                config_file.write_text("app:\n  output_dir: ${OUTPUT_DIR:-output}\n", encoding="utf-8")
                env_file.write_text("OUTPUT_DIR=custom-output\n", encoding="utf-8")

                config = load_config(config_file, env_file)

        self.assertEqual(config["app"]["output_dir"], "custom-output")

    def test_resolve_path_value_uses_base_dir(self) -> None:
        with TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            expected = tmp_path / "output" / "screenshots"

            self.assertEqual(resolve_path_value("output/screenshots", tmp_path), expected)


if __name__ == "__main__":
    unittest.main()
