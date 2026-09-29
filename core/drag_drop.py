import logging

import win32api
import win32con
import win32gui
from PyQt5.QtCore import QObject, QPoint, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QFrame


log = logging.getLogger("embedtab.drag_drop")


class _DropOverlay(QFrame):
    """Visual drop target covering the whole EmbedTab view."""

    def __init__(self, target_widget) -> None:
        super().__init__(target_widget)
        self._target_widget = target_widget
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setVisible(False)

    def sync_geometry(self) -> None:
        self.setGeometry(self._target_widget.rect())
        self.raise_()
        self.update()

    def paintEvent(self, event) -> None:
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(59, 130, 246, 35))
        pen = QPen(QColor(59, 130, 246, 220), 3, Qt.DashLine)
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(2, 2, -3, -3))
        painter.setPen(QColor(59, 130, 246, 255))
        font = painter.font()
        font.setBold(True)
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, "Release here to embed window")


class WindowDragEmbedController(QObject):
    """Detect an OS-level window drag and emit the source HWND on drop."""

    dropped = pyqtSignal(int)
    dragging_changed = pyqtSignal(bool)

    def __init__(self, target_widget, window_manager, parent=None) -> None:
        super().__init__(parent)
        self.target_widget = target_widget
        self.window_manager = window_manager
        self._timer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._poll)
        self._left_down = False
        self._source_hwnd = 0
        self._dragging = False
        self._target_hover = False
        self._overlay = _DropOverlay(target_widget)

    def start(self) -> None:
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()
        self._left_down = False
        self._source_hwnd = 0
        self._set_dragging(False)
        self._set_target_hover(False)

    def _poll(self) -> None:
        left_down = bool(win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000)
        if left_down and not self._left_down:
            self._begin_drag()
        elif not left_down and self._left_down:
            self._finish_drag()

        if self._dragging:
            self._set_target_hover(self._cursor_inside_target())
            if self._target_hover:
                self._overlay.sync_geometry()

        self._left_down = left_down

    def _begin_drag(self) -> None:
        self._source_hwnd = self._window_at_cursor()
        if not self._source_hwnd:
            return
        if self._is_inside_target(self._source_hwnd):
            self._source_hwnd = 0
            return
        if not self.window_manager.validate(self._source_hwnd):
            self._source_hwnd = 0
            return
        self._set_dragging(True)
        log.debug("Window drag started: hwnd=%s", self._source_hwnd)

    def _finish_drag(self) -> None:
        source_hwnd = self._source_hwnd
        self._source_hwnd = 0
        was_dragging = self._dragging
        inside_target = self._cursor_inside_target()
        self._set_dragging(False)
        self._set_target_hover(False)
        if not was_dragging or not source_hwnd or not inside_target:
            return
        if not self.window_manager.validate(source_hwnd):
            return
        log.info("Window dropped into EmbedTab: hwnd=%s", source_hwnd)
        self.dropped.emit(source_hwnd)

    def _window_at_cursor(self) -> int:
        try:
            point = win32api.GetCursorPos()
            hwnd = win32gui.WindowFromPoint(point)
            if not hwnd:
                return 0
            return int(win32gui.GetAncestor(hwnd, win32con.GA_ROOT) or hwnd)
        except Exception:
            log.debug("Unable to resolve window under cursor", exc_info=True)
            return 0

    def _cursor_inside_target(self) -> bool:
        try:
            x, y = win32api.GetCursorPos()
            return self.target_widget.rect().contains(
                self.target_widget.mapFromGlobal(QPoint(x, y))
            )
        except Exception:
            return False

    def _is_inside_target(self, hwnd: int) -> bool:
        try:
            target = int(self.target_widget.winId())
            return hwnd == target or bool(win32gui.IsChild(target, hwnd))
        except Exception:
            return False

    def _set_dragging(self, value: bool) -> None:
        if self._dragging == value:
            return
        self._dragging = value
        self.dragging_changed.emit(value)

    def _set_target_hover(self, value: bool) -> None:
        if self._target_hover == value:
            return
        self._target_hover = value
        self._overlay.setVisible(value)
        if value:
            self._overlay.sync_geometry()
