from typing import Callable

from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QSpinBox, QHBoxLayout, QDoubleSpinBox

from core.formulas.probabilities import (
    bernoulli,
    polynomial_distribution
)
from utils.paths import resolve_path
from utils.qt_utlis import show_error
from utils.widgets import TaskView


class Task1(TaskView):
    __current_param_collector: Callable[[], dict] | None = None
    __current_calculated_func: Callable[..., float] | None = None
    __current_restriction_checker: Callable[[], bool] | None = None

    __count_params_in_scrollbar = 1

    def __init__(self, task_number: int, parent):
        super().__init__(parent)
        self._task_number = task_number

        self.__init_ui()
        self.__bind_listeners()

        self.__selector_of_formula = {
            0: self.__on_bernoulli_formula_selected,
            1: self.__on_bernoulli_polynomial_formula_selected,
        }

    def task_name(self):
        return f"{self._task_number}. Формулы Бернулли и полиномиальной формулы"

    def __init_ui(self):
        uic.loadUi(resolve_path("ui/lab_3_task_1.ui"), self)
        self.__on_bernoulli_formula_selected()
        self.__on_selected_bernoulli_equal()

    def __bind_listeners(self):
        self.formula_selector.currentIndexChanged.connect(lambda idx_formula: self.__selector_of_formula[idx_formula]())

        self.bernulli_equal.clicked.connect(self.__on_selected_bernoulli_equal)
        self.bernulli_less.clicked.connect(self.__on_selected_bernoulli_less)
        self.bernulli_equal_or_greater.clicked.connect(self.__on_selected_bernoulli_equal_or_greater)
        self.bernulli_in_range.clicked.connect(self.__on_selected_bernoulli_in_range)

        self.polynomial_k_count.valueChanged.connect(self.__update_polynomial_params_in_scrollbar)

        self.bernoulli_n_count.valueChanged.connect(lambda val: self.bernulli_m_2.setMaximum(val))
        self.bernulli_m_2.valueChanged.connect(lambda val: self.bernulli_m_1.setMaximum(val))
        self.bernulli_m_1.valueChanged.connect(lambda val: self.bernulli_m_2.setMinimum(val))

        self.calculate_btn.clicked.connect(self.__on_clicked_calculate_button)

    def __on_bernoulli_formula_selected(self):
        self.polynomial_param_sidebar.hide()
        self.formula_img.setPixmap(QPixmap(
            resolve_path("res/images/lab3/bernoulli_formula_picture.png")
        ))
        self.bernoulli_params.show()
        self.bernulli_type_set.show()
        self.formula_view.show()
        self.__current_calculated_func = bernoulli

        self.limits_of_formula.setText(
            "Ограничения: m<= n."
        )
        self.__current_restriction_checker = self.__check_restrictions_bernoulli_formula
        self.__on_selected_bernoulli_equal()

    def __check_restrictions_bernoulli_formula(self) -> bool:
        return True  # not required due to restrictions set in the ui

    def __on_bernoulli_polynomial_formula_selected(self):
        self.polynomial_param_sidebar.show()
        self.formula_img.setPixmap(QPixmap(
            resolve_path("res/images/lab3/bernoulli_polynomial_formula_picture.png")
        ))
        self.bernoulli_params.hide()
        self.bernulli_type_set.hide()
        self.formula_view.hide()

        self.limits_of_formula.setText(
            "Ограничения:m<sub>1</sub> + m<sub>2</sub> + ... + m<sub>k</sub> = n. " +
            "p<sub>1</sub> + p<sub>2</sub> + ... + p<sub>k</sub = 1"
        )
        self.limits_of_formula.show()

        self.__current_param_collector = lambda: {
            "n": self.polynomial_n_count.value(),
            "m": [getattr(self, f"m_{num}").value() for num in range(1, self.__count_params_in_scrollbar + 1)],
            "p": [getattr(self, f"p_{num}").value() for num in range(1, self.__count_params_in_scrollbar + 1)]
        }
        self.__current_calculated_func = polynomial_distribution
        self.__current_restriction_checker = self.__check_restrictions_bernoulli_polynomial_formula

    def __check_restrictions_bernoulli_polynomial_formula(self) -> bool:

        msg = ''
        param = self.__current_param_collector()
        n, m, p = param["n"], param["m"], param["p"]
        if sum(m) != n:
            msg = "Не выполняется условие m<sub>1</sub> + m<sub>2</sub> + ... + m<sub>k</sub> = n"
        elif sum(p) != 1:
            msg = "Вероятности p<sub>1</sub> + p<sub>2</sub> + ... + p<sub>k</sub> ≠ 1. Не образуется полная группа событий."

        if msg == '': return True

        show_error(
            title="Ошибка",
            message=msg
        )

        return False

    def __on_selected_bernoulli_equal(self):
        self.bernulli_m_1.hide()
        self.bernulli_m_2.show()
        self.bernulli_formula_k.setText("k = ")
        self.__current_param_collector = lambda: {
            "p": self.bernoulli_p_count.value(),
            "n": self.bernoulli_n_count.value(),
            "min_successes": self.bernulli_m_2.value(),
            "max_successes": None
        }

    def __on_selected_bernoulli_less(self):
        self.bernulli_m_1.hide()
        self.bernulli_m_2.show()
        self.bernulli_formula_k.setText("k < ")
        self.__current_param_collector = lambda: {
            "p": self.bernoulli_p_count.value(),
            "n": self.bernoulli_n_count.value(),
            "min_successes": 0,
            "max_successes": self.bernulli_m_2.value() - 1  # тк по усл не влючительно
        }

    def __on_selected_bernoulli_equal_or_greater(self):
        self.bernulli_m_1.hide()
        self.bernulli_m_2.show()
        self.bernulli_formula_k.setText("k >= ")
        self.__current_param_collector = lambda: {
            "p": self.bernoulli_p_count.value(),
            "n": self.bernoulli_n_count.value(),
            "min_successes": self.bernulli_m_2.value(),
            "max_successes": self.bernoulli_n_count.value()
        }

    def __on_selected_bernoulli_in_range(self):
        self.bernulli_m_1.show()
        self.bernulli_m_2.show()
        self.bernulli_formula_k.setText(" <= k <= ")
        self.__current_param_collector = lambda: {
            "p": self.bernoulli_p_count.value(),
            "n": self.bernoulli_n_count.value(),
            "min_successes": self.bernulli_m_1.value(),
            "max_successes": self.bernulli_m_2.value()
        }

    def __update_polynomial_params_in_scrollbar(self):
        count = self.polynomial_k_count.value()

        # Adding new widgets
        for num in range(self.__count_params_in_scrollbar + 1, count + 1, 1):
            self.__add_new_m_p_spinbox(num)

        # Remove extra widgets
        for num in range(self.__count_params_in_scrollbar, count, -1):
            self.__remove_m_p_spinbox(num)

        self.__count_params_in_scrollbar = count

    def __add_new_m_p_spinbox(self, num: int):
        font = QFont()
        font.setPointSize(12)
        font.setKerning(True)

        m_spb_name = f'm_{num}'
        m_spb = QSpinBox()
        m_spb.setValue(0)
        m_spb.setPrefix(f'm{num} = ')
        m_spb.setObjectName(m_spb_name)
        m_spb.setFont(font)
        m_spb.setMinimum(0)
        m_spb.setSingleStep(1)

        p_sbp_name = f'p_{num}'
        p_spb = QDoubleSpinBox()
        p_spb.setValue(0.0)
        p_spb.setPrefix(f'p{num} = ')
        p_spb.setObjectName(p_sbp_name)
        p_spb.setFont(font)
        p_spb.setMaximum(1)
        p_spb.setDecimals(3)
        p_spb.setSingleStep(0.01)

        layout = QHBoxLayout()
        layout.addWidget(m_spb)
        layout.addWidget(p_spb)

        self.scrollAreaWidgetContents.layout().insertLayout(num - 1, layout)

        setattr(self, f'layout_{num}', layout)
        setattr(self, m_spb_name, m_spb)
        setattr(self, p_sbp_name, p_spb)

    def __remove_m_p_spinbox(self, num: int):
        spb = getattr(self, f'm_{num}')
        spb.setVisible(False)
        spb.disconnect()
        spb = getattr(self, f'p_{num}')
        spb.setVisible(False)
        spb.disconnect()
        delattr(self, f'layout_{num}')
        delattr(self, f'm_{num}')
        delattr(self, f'p_{num}')

    def __on_clicked_calculate_button(self):

        if not self.__current_restriction_checker():
            return

        kwargs: dict = self.__current_param_collector()
        try:
            result: float = self.__current_calculated_func(**kwargs)
        except ValueError as ve:
            print(ve)
            print(kwargs)
            return

        self.result.setText(f"{result}")
