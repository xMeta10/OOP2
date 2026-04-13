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


class NumberWidget(QWidget):
    value_changed = pyqtSignal(int)
    validation_request = pyqtSignal(int, object)  # значение, callback

    def __init__(self, label: str, min_val: int, max_val: int, initial_value: int = 0, is_b: bool = False):
        super().__init__()
        self.current_value = initial_value
        self.min_val = min_val
        self.max_val = max_val
        self.is_b = is_b
        self.a_value = 0
        self.c_value = 100

        layout = QVBoxLayout()
        layout.setSpacing(8)

        title = QLabel(label)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px; color: #e0e0e0;")
        layout.addWidget(title)

        self.text_edit = QLineEdit()
        self.text_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_edit.setValidator(QIntValidator(min_val, max_val))
        self.text_edit.setText(str(initial_value))
        self.text_edit.editingFinished.connect(self.on_editing_finished)
        self.text_edit.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.text_edit)

        self.spin_box = QSpinBox()
        self.spin_box.setRange(min_val, max_val)
        self.spin_box.setValue(initial_value)
        self.spin_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_box.valueChanged.connect(self.on_spin_changed)
        layout.addWidget(self.spin_box)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_val, max_val)
        self.slider.setValue(initial_value)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.slider)

        self.setLayout(layout)
        self._updating = False

        # Применяем стили к виджету
        self.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 6px;
                color: #ffffff;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #4caf50;
            }
            QSpinBox {
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 4px;
                color: #ffffff;
                font-size: 12px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 16px;
                border-radius: 3px;
                background-color: #2d2d2d;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #4caf50;
            }
        """)

    def set_bounds(self, a: int, c: int):
        self.a_value = a
        self.c_value = c

    def update_value(self, value: int):
        if self._updating:
            return

        self._updating = True
        self.current_value = value
        self.text_edit.setText(str(value))
        self.spin_box.setValue(value)
        self.slider.setValue(value)
        self._updating = False

    def on_text_changed(self, text: str):
        if self._updating:
            return
        try:
            if text and text != "-":
                value = int(text)
                if self.min_val <= value <= self.max_val:
                    if self.is_b and (value < self.a_value or value > self.c_value):
                        return
                    self.value_changed.emit(value)
        except ValueError:
            pass

    def on_editing_finished(self):
        if self._updating:
            return

        try:
            text = self.text_edit.text()
            if not text or text == "-":
                self.update_value(self.current_value)
                return

            value = int(text)
            if value < self.min_val or value > self.max_val:
                self.update_value(self.current_value)
                return

            if self.is_b and (value < self.a_value or value > self.c_value):
                self.update_value(self.current_value)
                return

        except ValueError:
            self.update_value(self.current_value)

    def on_spin_changed(self, value: int):
        if not self._updating:
            if self.is_b and (value < self.a_value or value > self.c_value):
                self.update_value(self.current_value)  # Откатываем
                return
            self.value_changed.emit(value)

    def on_slider_changed(self, value: int):
        if not self._updating:
            if self.is_b and (value < self.a_value or value > self.c_value):
                self.update_value(self.current_value)  # Откатываем
                return
            self.value_changed.emit(value)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.current_value != self.spin_box.value():
            self.update_value(self.current_value)


