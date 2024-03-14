from __future__ import annotations

from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QErrorMessage

from core.formulas.combinatorics import (
    permutation_without_rep,
    accommodations_without_rep
)
from utils.paths import resolve_path
from utils.widgets import TaskView


class Task2(TaskView):

    def __init__(self, task_number: int, parent):
        super().__init__(parent)
        self._task_number = task_number

        self.__init_ui()
        self.__bind_listeners()

    def __init_ui(self):
        uic.loadUi(resolve_path("ui/lab_1_task_2.ui"), self)
        self.__load_images()

    def __load_images(self):
        self.condition.setPixmap(QPixmap(resolve_path('res/images/lab1_condition_task_2.png')))
        self.formula.setPixmap(QPixmap(resolve_path('res/images/lab1_formula_task_2.png')))

    def __bind_listeners(self):
        self.calculate_button.clicked.connect(self.__calculate)

    def __calculate(self):
        n: int = self.n_count.value()
        m: int = self.m_count.value()
        result: float
        try:
            result = permutation_without_rep(m) / accommodations_without_rep(m, n)
        except ValueError as ve:
            error_dialog = QErrorMessage()
            error_dialog.showMessage(
                """Ошибка: n больше m"""
            )
            error_dialog.exec()
            return

        self.result.setText(str(result))

    def task_name(self):
        return "Задача 2"
