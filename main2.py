import sys
import json
import os
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QSpinBox, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QIntValidator, QFont


class Model(QObject):
    data_changed = pyqtSignal()

    MIN_VALUE = 0
    MAX_VALUE = 100

    def __init__(self):
        super().__init__()
        self._a = self.MIN_VALUE
        self._b = (self.MIN_VALUE + self.MAX_VALUE) // 2
        self._c = self.MAX_VALUE
        self._update_count = 0
        self._file_path = "model_data.json"

        self._load_without_notify()
        self._notify_change()

    def get_min_value(self) -> int:
        return self.MIN_VALUE

    def get_max_value(self) -> int:
        return self.MAX_VALUE

    def get_update_count(self) -> int:
        return self._update_count

    def _notify_change(self):
        self._update_count += 1
        self.data_changed.emit()

    def get_a(self) -> int:
        return self._a

    def get_b(self) -> int:
        return self._b

    def get_c(self) -> int:
        return self._c

    def set_a(self, value: int):
        old_a, old_b, old_c = self._a, self._b, self._c
        value = max(self.MIN_VALUE, min(self.MAX_VALUE, value))

        new_a = value
        new_b = self._b
        new_c = self._c

        if new_a > new_b:
            new_b = new_a
        if new_a > new_c:
            new_c = new_a
        if new_b > new_c:
            new_c = new_b

        self._a = new_a
        self._b = new_b
        self._c = new_c

        if (old_a, old_b, old_c) != (self._a, self._b, self._c):
            self._notify_change()

    def set_b(self, value: int):
        old_b = self._b
        value = max(self.MIN_VALUE, min(self.MAX_VALUE, value))

        if self._a <= value <= self._c:
            self._b = value
            if old_b != self._b:
                self._notify_change()

    def set_c(self, value: int):
        old_a, old_b, old_c = self._a, self._b, self._c
        value = max(self.MIN_VALUE, min(self.MAX_VALUE, value))

        new_c = value
        new_a = self._a
        new_b = self._b

        if new_c < new_b:
            new_b = new_c
        if new_c < new_a:
            new_a = new_c
        if new_a > new_b:
            new_b = new_a

        self._a = new_a
        self._b = new_b
        self._c = new_c

        if (old_a, old_b, old_c) != (self._a, self._b, self._c):
            self._notify_change()

    def set_all(self, a: int, b: int, c: int):
        old_a, old_b, old_c = self._a, self._b, self._c

        a = max(self.MIN_VALUE, min(self.MAX_VALUE, a))
        b = max(self.MIN_VALUE, min(self.MAX_VALUE, b))
        c = max(self.MIN_VALUE, min(self.MAX_VALUE, c))

        if a > c:
            a, c = c, a
        if b < a:
            b = a
        if b > c:
            b = c

        self._a = a
        self._b = b
        self._c = c

        if (old_a, old_b, old_c) != (self._a, self._b, self._c):
            self._notify_change()

    def save(self):
        try:
            data = {'a': self._a, 'b': self._b, 'c': self._c}
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")

    def _load_without_notify(self):
        try:
            if os.path.exists(self._file_path):
                with open(self._file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    a = max(self.MIN_VALUE, min(self.MAX_VALUE, data.get('a', self.MIN_VALUE)))
                    b = max(self.MIN_VALUE, min(self.MAX_VALUE, data.get('b', (self.MIN_VALUE + self.MAX_VALUE) // 2)))
                    c = max(self.MIN_VALUE, min(self.MAX_VALUE, data.get('c', self.MAX_VALUE)))

                    if a > c:
                        a, c = c, a
                    if b < a:
                        b = a
                    if b > c:
                        b = c

                    self._a = a
                    self._b = b
                    self._c = c
        except Exception as e:
            print(f"Ошибка при загрузке: {e}")
            self._a = self.MIN_VALUE
            self._b = (self.MIN_VALUE + self.MAX_VALUE) // 2
            self._c = self.MAX_VALUE


