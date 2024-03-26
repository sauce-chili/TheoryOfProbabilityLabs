from math import sqrt

from PyQt5 import uic
from PyQt5.QtGui import QPixmap

from utils.paths import resolve_path
from utils.widgets import TaskView
from core.formulas.probabilities import (
    bernoulli,
    local_moivre_laplace
)


class Task2(TaskView):
    x0_prefix = "x<sub>0</sub> = "
    P_prefix = "P<sub>n</sub>(m) = "

    def __init__(self, task_number: int, parent):
        super().__init__(parent)
        self._task_number = task_number

        self.__init_ui()
        self.__bind_listeners()

    def __init_ui(self):
        uic.loadUi(resolve_path('ui/lab_3_task_2.ui'), self)
        self.formula_img.setPixmap(QPixmap(
            resolve_path("res/images/lab3/local_moivre_laplace_formula_picture.png")
        ))

    def __bind_listeners(self):
        self.n_spinbox.valueChanged.connect(self.__n_value_changed)
        self.p_spinbox.valueChanged.connect(self.__p_value_changed)
        self.q_spinbox.valueChanged.connect(self.q_value_changed)
        self.m_spinbox.valueChanged.connect(self.__calculate)

    def __n_value_changed(self):
        self.m_spinbox.setMaximum(self.n_spinbox.value())
        self.__calculate()

    def __p_value_changed(self):
        self.q_spinbox.blockSignals(True)
        self.q_spinbox.setValue(round(1 - round(self.p_spinbox.value(), 3), 3))
        self.q_spinbox.blockSignals(False)
        self.__calculate()

    def q_value_changed(self):
        self.p_spinbox.blockSignals(True)
        self.p_spinbox.setValue(round(1 - round(self.q_spinbox.value(), 3), 3))
        self.p_spinbox.blockSignals(False)
        self.__calculate()

    def __calculate(self):
        n, p, m = self.n_spinbox.value(), self.p_spinbox.value(), self.m_spinbox.value()

        q = 1 - p

        P_bernoulli_result = bernoulli(p, n, m)

        # TODO найти ошибку в локальной функции муавра-лапласа
        x0 = (m - n * p) / sqrt(n * p * q)
        P_laplace_local_result = local_moivre_laplace(x0, n, p)

        self.x0.setText(self.x0_prefix + f"{x0}")
        self.laplace_local_result.setText(self.P_prefix + f"{P_laplace_local_result}")
        self.bernoulli_result.setText(self.P_prefix + f"{P_bernoulli_result}")

    def task_name(self):
        return f"{self._task_number}. Локальная теорема Муавра-Лапласа"
