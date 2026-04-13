import sys
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout
)
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QMouseEvent, QKeyEvent, QResizeEvent
from typing import List


class CCircle:

    def __init__(self, x: int, y: int, radius: int = 30):
        self._x = x
        self._y = y
        self._radius = radius
        self._is_selected = False

    def get_x(self) -> int:
        return self._x

    def get_y(self) -> int:
        return self._y

    def get_radius(self) -> int:
        return self._radius

    def is_selected(self) -> bool:
        return self._is_selected

    def set_selected(self, selected: bool):
        self._is_selected = selected

    def contains_point(self, x: int, y: int) -> bool:
        dx = x - self._x
        dy = y - self._y
        return (dx * dx + dy * dy) <= (self._radius * self._radius)

    def is_visible(self, widget_rect: QRect) -> bool:
        circle_rect = QRect(
            self._x - self._radius,
            self._y - self._radius,
            self._radius * 2,
            self._radius * 2
        )
        return widget_rect.intersects(circle_rect)

    def draw(self, painter: QPainter):
        if self._is_selected:
            painter.setBrush(QBrush(QColor(255, 0, 0, 150)))  # сильно красная заливка
            painter.setPen(QPen(QColor(255, 0, 0), 3))
        else:
            painter.setBrush(QBrush(QColor(200, 200, 200, 100)))
            painter.setPen(QPen(QColor(0, 0, 0), 2))

        painter.drawEllipse(self._x - self._radius,
                            self._y - self._radius,
                            self._radius * 2,
                            self._radius * 2)

class CircleContainer:

    def __init__(self):
        self._items: List[CCircle] = []

    def add(self, circle: CCircle):
        self._items.append(circle)

    def remove(self, index: int):
        if 0 <= index < len(self._items):
            del self._items[index]

    def get_count(self) -> int:
        return len(self._items)

    def get_object(self, index: int) -> CCircle:
        if 0 <= index < len(self._items):
            return self._items[index]
        raise IndexError("Index out of range")

    def get_all_selected(self) -> List[int]:
        return [i for i, circle in enumerate(self._items) if circle.is_selected()]

    def clear_selection(self):
        for circle in self._items:
            circle.set_selected(False)

    def __iter__(self):
        return iter(self._items)



