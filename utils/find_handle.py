# from time import sleep
# import psutil

from win32 import win32gui, win32process


def is_window(hwnd):
    return bool(win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd))


def enum_windows_callback(hwnd, windows):
    if is_window(hwnd):
        windows.append((hwnd, win32gui.GetWindowText(hwnd)))

def find_handle(title_window="GPM-Browser"):
    handles = []
    win32gui.EnumWindows(enum_windows_callback, handles)
    print(handles)
    handles = [title+"|"+str(hwnd) for hwnd, title in handles if title_window in title]
    return handles


def get_pid_from_handle(hwnd):
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return pid
