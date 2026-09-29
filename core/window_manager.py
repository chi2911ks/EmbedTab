from dataclasses import dataclass
from typing import List, Optional

import win32gui
import win32process


@dataclass(frozen=True)
class WindowInfo:
    hwnd: int
    title: str
    pid: int
    process_name: str = ""


class WindowManager:
    """Windows HWND discovery and lifecycle helpers."""

    @staticmethod
    def is_window(hwnd: int) -> bool:
        try:
            return bool(
                win32gui.IsWindow(hwnd)
                and win32gui.IsWindowVisible(hwnd)
                and win32gui.IsWindowEnabled(hwnd)
            )
        except (TypeError, ValueError):
            return False

    @staticmethod
    def get_pid(hwnd: int) -> int:
        _, pid = win32process.GetWindowThreadProcessId(int(hwnd))
        return pid

    def find(self, title: str = "", limit: Optional[int] = None) -> List[WindowInfo]:
        windows: List[WindowInfo] = []

        def callback(hwnd: int, _: object) -> None:
            if not self.is_window(hwnd):
                return
            window_title = win32gui.GetWindowText(hwnd)
            if title and title.lower() not in window_title.lower():
                return
            try:
                pid = self.get_pid(hwnd)
            except Exception:
                pid = 0
            windows.append(WindowInfo(hwnd, window_title, pid))

        win32gui.EnumWindows(callback, None)
        if limit is not None:
            return windows[:limit]
        return windows

    def find_by_pid(self, pid: int) -> List[WindowInfo]:
        return [window for window in self.find() if window.pid == int(pid)]

    def validate(self, hwnd: int) -> bool:
        return self.is_window(hwnd)

    def focus(self, hwnd: int) -> bool:
        if not self.is_window(hwnd):
            return False
        try:
            win32gui.SetForegroundWindow(hwnd)
            return True
        except Exception:
            return False

    def close(self, hwnd: int) -> bool:
        if not self.is_window(hwnd):
            return False
        try:
            win32gui.PostMessage(hwnd, win32gui.WM_CLOSE, 0, 0)
            return True
        except Exception:
            return False
