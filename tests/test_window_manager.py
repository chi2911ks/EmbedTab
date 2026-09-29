from core.window_manager import WindowInfo, WindowManager


def test_window_info():
    item = WindowInfo(10, "Chrome", 20)
    assert item.hwnd == 10
    assert item.pid == 20


def test_invalid_hwnd():
    assert WindowManager().validate(0) is False
