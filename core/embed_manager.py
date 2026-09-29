from dataclasses import dataclass
from typing import Dict, List, Optional

from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QWidget, QHBoxLayout


@dataclass
class EmbeddedWindow:
    index: int
    hwnd: int
    container: QWidget


class EmbedManager(QObject):
    def __init__(self, parent: QWidget, max_height: int = 500) -> None:
        super().__init__(parent)
        self.parent_widget = parent
        self.max_height = max_height
        self._items: Dict[int, EmbeddedWindow] = {}
        self._next_index = 0

    def indexes(self) -> List[int]: return sorted(self._items)
    def contains(self, index: int) -> bool: return int(index) in self._items
    def get(self, index: int) -> Optional[EmbeddedWindow]: return self._items.get(int(index))
    def containers(self) -> Dict[int, QWidget]: return {i: item.container for i, item in self._items.items()}

    def _clear_container(self, container: QWidget) -> None:
        layout = container.layout()
        if layout is None: return
        for i in reversed(range(layout.count())):
            child = layout.itemAt(i).widget()
            if child is not None:
                child.setParent(None)
                child.deleteLater()

    def attach(self, index: int, hwnd: int) -> EmbeddedWindow:
        item = self._items[int(index)]
        self._clear_container(item.container)
        qwindow = QWindow.fromWinId(int(hwnd))
        embedded = QWidget.createWindowContainer(qwindow, item.container)
        embedded.setFocusPolicy(Qt.NoFocus)
        embedded.setMinimumHeight(self.max_height)
        embedded.setMaximumHeight(self.max_height)
        item.container.layout().addWidget(embedded)
        item.hwnd = int(hwnd)
        item.container.show()
        return item

    def create(self) -> int:
        index = self._next_index
        self._next_index += 1
        container = QWidget(self.parent_widget)
        container.setMinimumHeight(self.max_height)
        container.setMaximumHeight(self.max_height)
        container.setLayout(QHBoxLayout())
        self._items[index] = EmbeddedWindow(index, 0, container)
        return index

    def create_and_attach(self, hwnd: int) -> EmbeddedWindow:
        return self.attach(self.create(), hwnd)

    def remove(self, index: int) -> bool:
        item = self._items.pop(int(index), None)
        if item is None: return False
        item.container.setParent(None)
        item.container.deleteLater()
        return True

    def clear(self) -> int:
        indexes = list(self._items)
        for index in indexes: self.remove(index)
        return len(indexes)

    def find_by_hwnd(self, hwnd: int) -> Optional[EmbeddedWindow]:
        return next((x for x in self._items.values() if x.hwnd == int(hwnd)), None)

    def snapshot(self, window_manager=None) -> List[dict]:
        return [
            {"index": x.index, "hwnd": x.hwnd, "valid": bool(window_manager.validate(x.hwnd)) if window_manager and x.hwnd else False}
            for x in self._items.values()
        ]
