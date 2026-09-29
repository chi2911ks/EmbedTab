from PyQt5.QtCore import QObject, QTimer, pyqtSignal


class WindowMonitor(QObject):
    changed = pyqtSignal(object)

    def __init__(self, window_manager, interval_ms=1000, parent=None):
        super().__init__(parent)
        self.window_manager = window_manager
        self.interval_ms = max(250, int(interval_ms))
        self._tracked = {}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check)

    def track(self, index, hwnd, title=""):
        self._tracked[int(index)] = {"hwnd": int(hwnd), "title": title}

    def untrack(self, index): self._tracked.pop(int(index), None)
    def start(self): self.timer.start(self.interval_ms)
    def stop(self): self.timer.stop()

    def check(self):
        lost = [index for index, item in self._tracked.items() if not self.window_manager.validate(item["hwnd"])]
        if lost: self.changed.emit(lost)

    def metadata(self, index): return self._tracked.get(int(index), {})
