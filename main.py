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

class DrawingWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._container = CircleContainer()
        self._ctrl_pressed = False
        self.setMinimumSize(400, 300)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.GlobalColor.white)
        self.setPalette(palette)

    def get_container(self) -> CircleContainer:
        return self._container

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        visible_rect = self.rect()

        for circle in self._container:
            if circle.is_visible(visible_rect):
                circle.draw(painter)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()

            clicked_circles = []
            for i, circle in enumerate(self._container):
                if circle.contains_point(pos.x(), pos.y()):
                    clicked_circles.append(i)

            if clicked_circles:
                if self._ctrl_pressed:
                    # Ctrl: переключение выделения
                    for idx in clicked_circles:
                        circle = self._container.get_object(idx)
                        circle.set_selected(not circle.is_selected())
                else:
                    # Без Ctrl: выделяем кликнутые объекты, остальные снимаем
                    self._container.clear_selection()
                    for idx in clicked_circles:
                        self._container.get_object(idx).set_selected(True)
            else:
                new_circle = CCircle(pos.x(), pos.y())
                self._container.add(new_circle)

            self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Control:
            self._ctrl_pressed = True
        elif event.key() == Qt.Key.Key_Delete:
            selected_indices = self._container.get_all_selected()

            for idx in reversed(selected_indices):
                self._container.remove(idx)

            self.update()
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Control:
            self._ctrl_pressed = False
        else:
            super().keyReleaseEvent(event)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.update()


