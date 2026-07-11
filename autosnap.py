"""自动截屏工具

用途：
  按照配置文件中设定的时间间隔自动截取屏幕画面，并将图片保存到指定输出目录。
  入口脚本只负责加载配置、初始化日志、创建运行上下文并调用 auto_snap 编排流程。

配置文件：
  默认读取项目根目录下的 config.yaml，配置截图间隔、截图次数、输出目录、文件名模板和图片格式。
  固定屏幕固定区域截图时，可先运行 list_screens.py 获取 screen_index，再在 region 中填写屏幕内坐标。
  如存在 common.env，会先读取其中的本机环境变量；该文件用于覆盖本机路径和调试参数，不进入版本库。

可选参数：
  --config-file   指定配置文件名或相对路径，默认 config.yaml。

示例：
  python autosnap.py
  python autosnap.py --config-file config.yaml

输出：
  截图文件默认写入 output/screenshots/，日志默认写入 log/autosnap.log。
  capture_count 为 0 时持续运行，按 Ctrl+C 停止。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from logging_config import get_logger
from pyautosnap.bootstrap import bootstrap_context
from pyautosnap.flows.auto_snap import run

logger = get_logger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run timed screenshot capture.")
    parser.add_argument("--config-file", default="config.yaml", help="Config file path relative to project root.")
    args = parser.parse_args()

    try:
        context = bootstrap_context(__file__, config_file=args.config_file)
        results = run(context)
    except Exception:
        logger.exception("Auto screenshot flow failed")
        return 1

    summary = {
        "captured": len(results),
        "files": [str(result.path) for result in results],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
