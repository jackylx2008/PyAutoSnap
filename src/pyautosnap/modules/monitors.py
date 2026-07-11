"""Windows monitor enumeration helpers."""

from __future__ import annotations

import ctypes
import platform
from dataclasses import dataclass
from ctypes import wintypes


MONITORINFOF_PRIMARY = 0x00000001
CCHDEVICENAME = 32


@dataclass(frozen=True)
class MonitorInfo:
    """One monitor's virtual desktop geometry."""

    index: int
    device_name: str
    left: int
    top: int
    right: int
    bottom: int
    is_primary: bool

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top


class RECT(ctypes.Structure):
    """Windows RECT structure."""

    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class MONITORINFOEXW(ctypes.Structure):
    """Windows MONITORINFOEXW structure."""

    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", wintypes.DWORD),
        ("szDevice", wintypes.WCHAR * CCHDEVICENAME),
    ]


def list_monitors() -> list[MonitorInfo]:
    """Return all Windows monitors with 1-based indexes used by config."""
    if platform.system().lower() != "windows":
        raise RuntimeError("Monitor enumeration is currently implemented for Windows only.")

    raw_monitors: list[MonitorInfo] = []
    user32 = ctypes.windll.user32

    monitor_enum_proc = ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        wintypes.HMONITOR,
        wintypes.HDC,
        ctypes.POINTER(RECT),
        wintypes.LPARAM,
    )

    def _callback(
        monitor_handle: wintypes.HMONITOR,
        _device_context: wintypes.HDC,
        _rect_pointer: ctypes.POINTER(RECT),
        _data: wintypes.LPARAM,
    ) -> bool:
        info = MONITORINFOEXW()
        info.cbSize = ctypes.sizeof(MONITORINFOEXW)
        if not user32.GetMonitorInfoW(monitor_handle, ctypes.byref(info)):
            raise ctypes.WinError()
        rect = info.rcMonitor
        raw_monitors.append(
            MonitorInfo(
                index=0,
                device_name=str(info.szDevice),
                left=int(rect.left),
                top=int(rect.top),
                right=int(rect.right),
                bottom=int(rect.bottom),
                is_primary=bool(info.dwFlags & MONITORINFOF_PRIMARY),
            )
        )
        return True

    if not user32.EnumDisplayMonitors(None, None, monitor_enum_proc(_callback), 0):
        raise ctypes.WinError()

    sorted_monitors = sorted(raw_monitors, key=lambda monitor: (not monitor.is_primary, monitor.left, monitor.top))
    return [
        MonitorInfo(
            index=index,
            device_name=monitor.device_name,
            left=monitor.left,
            top=monitor.top,
            right=monitor.right,
            bottom=monitor.bottom,
            is_primary=monitor.is_primary,
        )
        for index, monitor in enumerate(sorted_monitors, start=1)
    ]


def get_monitor(screen_index: int) -> MonitorInfo:
    """Return one monitor by the 1-based index printed by list_screens.py."""
    monitors = list_monitors()
    for monitor in monitors:
        if monitor.index == screen_index:
            return monitor
    available = ", ".join(str(monitor.index) for monitor in monitors)
    raise ValueError(f"Unknown screen_index: {screen_index}. Available indexes: {available}")
