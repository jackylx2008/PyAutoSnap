"""Visual feedback helpers for capture regions."""

from __future__ import annotations

import ctypes
import platform
import time
from ctypes import wintypes

from pyautosnap.modules.monitors import list_monitors


WS_POPUP = 0x80000000
WS_EX_LAYERED = 0x00080000
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TRANSPARENT = 0x00000020
LWA_ALPHA = 0x00000002
SW_HIDE = 0
SW_SHOWNOACTIVATE = 4
WM_DESTROY = 0x0002
COLOR_RED = 0x000000FF
FLASH_CLASS_NAME = "PyAutoSnapCaptureFlashWindow"
LRESULT = ctypes.c_ssize_t

_WND_PROC = None
_BACKGROUND_BRUSH = None
_CLASS_REGISTERED = False


class WNDCLASSW(ctypes.Structure):
    """Windows WNDCLASSW structure."""

    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", ctypes.c_void_p),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HANDLE),
        ("hCursor", wintypes.HANDLE),
        ("hbrBackground", wintypes.HANDLE),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]


def flash_capture_region(
    region: tuple[int, int, int, int] | None,
    cycles: int = 2,
    duration_ms: int = 160,
    hold_ms: int = 0,
    border_width: int = 6,
    alpha: int = 220,
) -> None:
    """Flash a red border around the captured area on Windows, then optionally keep it visible."""
    if platform.system().lower() != "windows":
        return
    if cycles <= 0 and hold_ms <= 0:
        return
    if cycles > 0 and duration_ms <= 0:
        return

    left, top, right, bottom = region or _virtual_screen_region()
    width = right - left
    height = bottom - top
    if width <= 0 or height <= 0:
        return

    border_width = max(1, min(border_width, width, height))
    alpha = max(1, min(alpha, 255))
    rects = [
        (left, top, width, border_width),
        (left, bottom - border_width, width, border_width),
        (left, top, border_width, height),
        (right - border_width, top, border_width, height),
    ]
    handles = [_create_flash_window(x, y, rect_width, rect_height, alpha) for x, y, rect_width, rect_height in rects]
    try:
        for _ in range(cycles):
            for handle in handles:
                ctypes.windll.user32.ShowWindow(handle, SW_SHOWNOACTIVATE)
                ctypes.windll.user32.UpdateWindow(handle)
            time.sleep(duration_ms / 1000)
            for handle in handles:
                ctypes.windll.user32.ShowWindow(handle, SW_HIDE)
            time.sleep(duration_ms / 1000)
        if hold_ms > 0:
            for handle in handles:
                ctypes.windll.user32.ShowWindow(handle, SW_SHOWNOACTIVATE)
                ctypes.windll.user32.UpdateWindow(handle)
            time.sleep(hold_ms / 1000)
    finally:
        for handle in handles:
            ctypes.windll.user32.DestroyWindow(handle)


def _virtual_screen_region() -> tuple[int, int, int, int]:
    monitors = list_monitors()
    left = min(monitor.left for monitor in monitors)
    top = min(monitor.top for monitor in monitors)
    right = max(monitor.right for monitor in monitors)
    bottom = max(monitor.bottom for monitor in monitors)
    return (left, top, right, bottom)


def _create_flash_window(x: int, y: int, width: int, height: int, alpha: int) -> int:
    _register_flash_window_class()
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    window = user32.CreateWindowExW(
        WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_TOOLWINDOW | WS_EX_TRANSPARENT,
        FLASH_CLASS_NAME,
        "",
        WS_POPUP,
        x,
        y,
        width,
        height,
        None,
        None,
        kernel32.GetModuleHandleW(None),
        None,
    )
    if not window:
        raise ctypes.WinError()
    if not user32.SetLayeredWindowAttributes(window, COLOR_RED, alpha, LWA_ALPHA):
        raise ctypes.WinError()
    return int(window)


def _register_flash_window_class() -> None:
    global _WND_PROC, _BACKGROUND_BRUSH, _CLASS_REGISTERED
    if _CLASS_REGISTERED:
        return

    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    kernel32 = ctypes.windll.kernel32
    user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.DefWindowProcW.restype = LRESULT
    wndproc_type = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

    def _window_proc(hwnd: wintypes.HWND, msg: wintypes.UINT, wparam: wintypes.WPARAM, lparam: wintypes.LPARAM) -> int:
        if msg == WM_DESTROY:
            return 0
        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    _WND_PROC = wndproc_type(_window_proc)
    _BACKGROUND_BRUSH = gdi32.CreateSolidBrush(COLOR_RED)
    window_class = WNDCLASSW()
    window_class.lpfnWndProc = ctypes.cast(_WND_PROC, ctypes.c_void_p).value
    window_class.hInstance = kernel32.GetModuleHandleW(None)
    window_class.hbrBackground = _BACKGROUND_BRUSH
    window_class.lpszClassName = FLASH_CLASS_NAME

    atom = user32.RegisterClassW(ctypes.byref(window_class))
    if not atom:
        error_code = ctypes.GetLastError()
        if error_code != 1410:
            raise ctypes.WinError(error_code)
    _CLASS_REGISTERED = True
