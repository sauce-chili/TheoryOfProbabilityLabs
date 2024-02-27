from __future__ import annotations

from typing import Callable

from PyQt5 import uic
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QSpinBox, QHBoxLayout, QErrorMessage, QWidget

from core.formulas.combinatorics import (
    accommodations_with_rep,
    combinations_without_rep,
    permutations_with_rep
)
from utils.paths import resolve_path
from widgets import TaskView


class Lab1(TaskView):
    __limit_label: str = "Ограничения:\n"
    __limit_of_combinations_without_rep: str = __limit_label + "В данной формуле m <= n"
    __limit_of_accommodations_with_rep: str = __limit_label + "В данной формуле нет ограничений"
    __limit_of_permutationsWithRep: str = __limit_label + "В данной формуле (m1 + m2 + ... + mk) = n И k <= n"

    __count_m_param_in_scroll_bar = 1  # TODO мб нахер не нужно и будет вытягивать значение c ui

    __current_func_param_collector: Callable[[], dict] | None = None
    __current_calculated_func: Callable[..., int] | None = None

    def __init__(self, task_number: int, parent):
        super().__init__(parent)
        self._task_number = task_number

        self.__init_ui()
        self.__bind_listener()

        self.__selector_of_formula = {
            0: self.__on_selected_formula_combinations_without_rep,
            1: self.__on_selected_formula_accommodations_with_rep,
            2: self.__on_selected_formula_permutations_with_rep
        }

    def __init_ui(self):
        uic.loadUi(resolve_path("ui/lab_1.ui"), self)

        self.__load_formulas_images()

        # По умолчанию выбрана первая формула
        self.__on_selected_formula_combinations_without_rep()
        # Скрываем остальные 2 формулы
        self.formula_accommodations_with_rep.hide()
        self.formula_permutations_with_rep.hide()

    def __load_formulas_images(self):
        self.formula_combinations_without_rep.setPixmap(QPixmap(resolve_path('res/images/lab1_formula1.png')))
        self.formula_accommodations_with_rep.setPixmap(QPixmap(resolve_path('res/images/lab1_formula2.png')))
        self.formula_permutations_with_rep.setPixmap(QPixmap(resolve_path('res/images/lab1_formula3.png')))

    def __bind_listener(self):
        self.formula_selector.currentIndexChanged.connect(self.__on_formula_changed)
        self.k_count.valueChanged.connect(self.__update_m_params_scroll_bar)
        self.calculate_btn.clicked.connect(self.__on_clicked_calculate_button)

    def __on_formula_changed(self, index_of_formula: int):
        # Скрыть все формулы
        self.__set_formulas_visibility(visibility=False)
        # Отобразить все параметры
        self.__show_of_all_parameters()
        # Обработка выбранной формулы
        self.__selector_of_formula[index_of_formula]()

    def __on_selected_formula_combinations_without_rep(self):
        self.formula_combinations_without_rep.show()
        # self.k_count.setValue(1)
        # Прячем ненужные параметры
        self.k_count_widget.hide()
        self.scrollArea.hide()
        # Отобразить ограничения данной формулы
        self.limits_of_formula.setText(self.__limit_of_combinations_without_rep)

        self.__current_calculated_func = combinations_without_rep
        self.__current_func_param_collector = self.__collect_param_for_combinations_without_rep

    def __on_selected_formula_accommodations_with_rep(self):
        self.formula_accommodations_with_rep.show()
        # self.k_count.setValue(1)
        # Прячем ненужные параметры
        self.k_count_widget.hide()
        self.scrollArea.hide()
        # Отобразить ограничения данной формулы
        self.limits_of_formula.setText(self.__limit_of_accommodations_with_rep)

        self.__current_calculated_func = accommodations_with_rep
        self.__current_func_param_collector = self.__collect_param_for_accommodations_with_rep

    def __on_selected_formula_permutations_with_rep(self):
        self.formula_permutations_with_rep.show()
        # self.m_count.setValue(1)
        # Прячем ненужный параметр
        self.m_count_widget.hide()
        # Отобразить ограничения данной формулы
        self.limits_of_formula.setText(self.__limit_of_permutationsWithRep)

        self.__current_calculated_func = permutations_with_rep
        self.__current_func_param_collector = self.__collect_param_for_permutations_with_rep

    def __collect_param_for_combinations_without_rep(self) -> dict:
        n: int = self.n_count.value()
        m: int = self.m_count.value()

        kwargs = {"n": n, "m": m}

        return kwargs

    def __collect_param_for_accommodations_with_rep(self) -> dict:
        n: int = self.n_count.value()
        m: int = self.m_count.value()

        kwargs = {"n": n, "m": m}

        return kwargs

    def __collect_param_for_permutations_with_rep(self) -> dict:
        n: int = self.n_count.value()

        m_list: list[int] = self.__collect_m_params()

        kwargs = {"n": n, "m": m_list}

        return kwargs

    def __set_formulas_visibility(self, visibility=True):

        set_visibility: Callable[[QWidget], None] = \
            lambda qw: qw.show() if visibility else qw.hide()

        set_visibility(self.formula_combinations_without_rep)
        set_visibility(self.formula_permutations_with_rep)
        set_visibility(self.formula_accommodations_with_rep)

    def __update_m_params_scroll_bar(self):
        count = self.k_count.value()

        # Adding new widgets
        for num in range(self.__count_m_param_in_scroll_bar + 1, count + 1, 1):
            self.__add_new_m_spinbox(num)

        # Remove extra widgets
        for num in range(self.__count_m_param_in_scroll_bar, count, -1):
            self.__remove_m_spinbox(num)

        self.__count_m_param_in_scroll_bar = count
        # TODO мб это нужно для вывода ограничения о сумме динамически
        # self.pm1.valueChanged.emit(self.pm1.value())

    def __show_of_all_parameters(self):
        self.k_count_widget.show()
        self.n_count_widget.show()
        self.m_count_widget.show()
        self.scrollArea.show()

    def __add_new_m_spinbox(self, num: int):
        font = QFont()
        font.setPixelSize(15)

        m_spb = QSpinBox()
        m_spb.setValue(0)
        m_spb.setPrefix(f'm{num} = ')
        m_spb.setObjectName(f'pm{num}')
        m_spb.setFont(font)
        m_spb.setMinimum(0)
        m_spb.setMaximum(1000)
        m_spb.setSingleStep(1)
        # m_spb.valueChanged.connect(self.__on_change_value_of_pm)  # TODO добавь слушателя

        layout = QHBoxLayout()
        layout.addWidget(m_spb)

        self.scrollAreaWidgetContents.layout().insertLayout(num - 1, layout)

        setattr(self, f'layout_{num}', layout)
        setattr(self, f'pm{num}', m_spb)

    def __remove_m_spinbox(self, num: int):
        spb = getattr(self, f'pm{num}')
        spb.setVisible(False)
        spb.disconnect()
        delattr(self, f'layout_{num}')
        delattr(self, f'pm{num}')

    def __collect_m_params(self) -> list[int]:
        return [
            getattr(self, f"pm{num}").value()
            for num in range(1, self.__count_m_param_in_scroll_bar + 1)
        ]

    def __on_clicked_calculate_button(self):
        kwargs: dict = self.__current_func_param_collector()
        try:
            result: int = self.__current_calculated_func(**kwargs)
        except ValueError as ve:
            error_dialog = QErrorMessage()
            error_dialog.showMessage(self.limits_of_formula.text())
            error_dialog.exec()
            return

        self.result.setText(str(result))

    def task_name(self):
        return "Элементы комбинаторики. Классическое определение вероятности"
