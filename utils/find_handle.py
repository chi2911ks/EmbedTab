from core.window_manager import WindowManager


_window_manager = WindowManager()


def is_window(hwnd):
    return _window_manager.is_window(hwnd)


def find_handle(title_window="Chrome"):
    return [
        f"{window.title}:{window.hwnd}"
        for window in _window_manager.find(title_window)
    ]


def get_pid_from_handle(hwnd):
    return _window_manager.get_pid(hwnd)
