from PyQt5 import uic
from PyQt5.QtGui import QPixmap

from core.formulas.combinatorics import combinations_without_rep as C_mn
from utils.paths import resolve_path
from utils.qt_utlis import show_error
from utils.widgets import TaskView


class Task3(TaskView):

    def __init__(self, task_number: int, parent):
        super().__init__(parent)
        self._task_number = task_number

        self.__init_ui()
        self.__bind_listeners()

    def __init_ui(self):
        uic.loadUi(resolve_path("ui/lab_2_task_3.ui"), self)
        self.__load_images()

    def __load_images(self):
        self.text_of_task.setPixmap(QPixmap(resolve_path('res/images/lab2/pics_lab_2/text_of_task.png')))
        self.h1_formula.setPixmap(QPixmap(resolve_path('res/images/lab2/pics_lab_2/h1.png')))
        self.h2_formula.setPixmap(QPixmap(resolve_path('res/images/lab2/pics_lab_2/h2.png')))
        self.a1_formula.setPixmap(QPixmap(resolve_path('res/images/lab2/pics_lab_2/punct_a.png')))
        self.a2_formula.setPixmap(QPixmap(resolve_path('res/images/lab2/pics_lab_2/punct_b.png')))
        self.h3_formula.setPixmap(QPixmap(resolve_path('res/images/lab2/pics_lab_2/h3.png')))
        self.a3_formula.setPixmap(QPixmap(resolve_path('res/images/lab2/pics_lab_2/punct_c.png')))
        self.a4_formula.setPixmap(QPixmap(resolve_path('res/images/lab2/pics_lab_2/punct_d.png')))

    def __bind_listeners(self):
        self.calculate_button.clicked.connect(self.__calculate)

    def __calculate(self):
        n_count: int = self.n_count.value()
        m1_count: int = self.m1_count.value()
        m2_count: int = self.m2_count.value()

        try:
            P_h1_m1 = self.__calculate_ph_m(n_count, m1_count)
            P_h2_m2 = self.__calculate_ph_m(n_count, m2_count)
        except ValueError as ve:
            show_error(
                title="Неверные параметры",
                message="m1 и m2 должны быть не больше n"
            )
            return

        P_a1 = P_h1_m1 * P_h2_m2

        P_a2 = P_h1_m1 * (1 - P_h2_m2)

        P_h3 = (1 - P_h1_m1) * P_h2_m2

        P_a3 = P_a2 + P_h3

        P_a4 = 1 - (1 - P_h1_m1) * (1 - P_h2_m2)

        self.h1_probability.setText(str(P_h1_m1))
        self.h2_probability.setText(str(P_h2_m2))
        self.h3_probability.setText(str(P_h3))
        self.a1_probability.setText(str(P_a1))
        self.a2_probability.setText(str(P_a2))
        self.a3_probability.setText(str(P_a3))
        self.a4_probability.setText(str(P_a4))

    def __calculate_ph_m(self, n: int, m: int) -> float:
        # Вероятность, что студент ответит не менее чем на два вопроса из n билетов, при условии, что выучил m
        return (
                (C_mn(2, m) * C_mn(1, n - m) + C_mn(3, m))
                /
                (C_mn(3, n))
        )

    def task_name(self):
        return f"{self._task_number}. Выбор подходящих промежуточных событий и использование операций над событиями"
