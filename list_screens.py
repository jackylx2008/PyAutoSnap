"""屏幕坐标查看工具

用途：
  在 Windows 11 扩展桌面环境下列出每个显示器的虚拟桌面坐标、分辨率、设备名和主屏标记。
  输出中的 index 可直接写入 config.yaml 的 flows.auto_snap.region.screen_index。

配置文件：
  本工具不读取 config.yaml 或 common.env，只调用 Windows 显示器枚举接口。

示例：
  python list_screens.py

输出：
  在控制台打印每个屏幕的 index、device、primary、left、top、width、height、right、bottom。
  配置固定屏幕区域截图时，使用 screen_index 加屏幕内 left/top/width/height。
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pyautosnap.modules.monitors import list_monitors


def main() -> int:
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
