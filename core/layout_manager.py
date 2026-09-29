from typing import Dict, Tuple


class LayoutManager:
    def __init__(self, grid_layout, columns=3):
        self.grid = grid_layout
        self.columns = max(1, int(columns))
        self.grid.setProperty("embed_columns", self.columns)

    def set_columns(self, columns):
        self.columns = max(1, int(columns))
        self.grid.setProperty("embed_columns", self.columns)
        return self.columns

    def position(self, count: int) -> Tuple[int, int]:
        return divmod(count, self.columns)

    def reflow(self, containers: Dict[int, object]):
        for container in containers.values(): self.grid.removeWidget(container)
        for position, index in enumerate(sorted(containers)):
            row, column = divmod(position, self.columns)
            self.grid.addWidget(containers[index], row, column)

    def available_columns(self, width: int, min_width=320) -> int:
        return max(1, int(width) // max(1, min_width))

    def swap(self, containers: Dict[int, object], first: int, second: int):
        if first not in containers or second not in containers:
            return False
        ordered = sorted(containers)
        a, b = ordered.index(first), ordered.index(second)
        ordered[a], ordered[b] = ordered[b], ordered[a]
        for container in containers.values(): self.grid.removeWidget(container)
        for position, index in enumerate(ordered):
            row, column = divmod(position, self.columns)
            self.grid.addWidget(containers[index], row, column)
        return True
