"""屏幕坐标查看工具

用途：
  在 Windows 11 扩展桌面环境下列出每个显示器的虚拟桌面坐标、分辨率、设备名和主屏标记。
  输出中的 index 可直接写入 config.yaml 的 flows.auto_snap.region.screen_index。
  同时截取一张包含所有屏幕的全屏截图，保存到项目根目录 test/ 下，用于辅助确认屏幕排列和截图坐标。

配置文件：
  本工具不读取 config.yaml 或 common.env，只调用 Windows 显示器枚举接口。

示例：
  python list_screens.py
  python list_screens.py --no-screenshot

输出：
  在控制台打印每个屏幕的 index、device、primary、left、top、width、height、right、bottom。
  默认额外输出全屏截图文件路径，文件名形如 fullscreen_20260711_170000_0001.png。
  配置固定屏幕区域截图时，使用 screen_index 加屏幕内 left/top/width/height。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pyautosnap.modules.monitors import list_monitors
from pyautosnap.modules.screenshot import ScreenshotSettings, capture_screenshot


def main() -> int:
    parser = argparse.ArgumentParser(description="List Windows monitor coordinates and capture a full-screen reference image.")
    parser.add_argument(
        "--no-screenshot",
        action="store_true",
        help="Only list monitors; do not save a full-screen reference screenshot.",
    )
    args = parser.parse_args()

    monitors = list_monitors()
    for monitor in monitors:
        primary = "yes" if monitor.is_primary else "no"
        print(
            "index={index} device={device} primary={primary} "
            "left={left} top={top} width={width} height={height} right={right} bottom={bottom}".format(
                index=monitor.index,
                device=monitor.device_name,
                primary=primary,
                left=monitor.left,
                top=monitor.top,
                width=monitor.width,
                height=monitor.height,
                right=monitor.right,
                bottom=monitor.bottom,
            )
        )

    if not args.no_screenshot:
        result = capture_screenshot(
            ScreenshotSettings(
                output_dir=PROJECT_ROOT / "test",
                image_format="png",
                filename_template="fullscreen_{timestamp}_{sequence:04d}.{extension}",
                region=None,
                all_screens=True,
            ),
            sequence=1,
        )
        print(f"fullscreen_screenshot={result.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
