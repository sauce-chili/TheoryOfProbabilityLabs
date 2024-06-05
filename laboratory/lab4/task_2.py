from utils.widgets import TaskView
from utils.paths import resolve_path
from utils.files import load_text_file, parse_statistic_file
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QTableWidgetItem
from utils.plots import *
from traceback import print_exc
from core.formulas.statistics import *
from PyQt5.QtGui import QPixmap

from PyQt5.QtWidgets import (
    QMessageBox,
    QVBoxLayout,
    QTableWidgetItem,
    QAbstractItemView
)


class Task2(TaskView):
    def __init__(self, task_number: int, parent):
        super().__init__(parent)
        self._task_number: int = task_number
        self.data = None

        uic.loadUi(resolve_path('ui/lab_4_task_2.ui'), self)
        self.__load_images()

        self.manual_input()
        self.calculateButton.clicked.connect(self.calculate)
        self.table.setRowCount(2)
        self.table.setColumnCount(0)
        self.table.setVerticalHeaderLabels(['xi', 'pi'])
        self.prepare_plots()

    def __load_images(self):
        self.expected_value_pic.setPixmap(QPixmap(resolve_path('res/images/lab4/expected_value_poisson.png')))
        self.dispersion_pic.setPixmap(QPixmap(resolve_path('res/images/lab4/dispersion_poisson.png')))
        self.sigma_pic.setPixmap(QPixmap(resolve_path('res/images/lab4/sigma_poisson.png')))
        self.moda_pic.setPixmap(QPixmap(resolve_path('res/images/lab4/moda_poisson.png')))

    def prepare_plots(self):  # o
        lt = QVBoxLayout()
        self.distribution_polygon_plot = Polygon(self, name='Многоугольник распределения')  # ака полигон частот
        lt.addWidget(self.distribution_polygon_plot, alignment=Qt.Alignment())
        self.distribution_polygon.setLayout(lt)

        lt = QVBoxLayout()
        self.discrete_function_graph = Function(self, name='Эмпирическая функция распределения')
        lt.addWidget(self.discrete_function_graph, alignment=Qt.Alignment())
        self.discrete_function_plot.setLayout(lt)

    def calculate(self):
        x_count = self.xCount.value()
        p = self.probabilityOfSuccess.value()
        try:
            poisson_data = self.read_manual_data()

            # if (sum(distribution_data.P) > 1.05 or sum(distribution_data.P) < 0.95):
            #     raise ValueError(f'Вероятность не равна приблизительно единице: {sum(distribution_data.P)}')

            if x_count < 100:
                raise ValueError(f'Кол-во испытаний должно быть не менее 100')

            if p > 0.1:
                raise ValueError(f'Вероятность должна быть меньше 0.1')

            if x_count * p >= 10:
                raise ValueError(f'np должно быть меньше 10')

            if x_count * p * (1 - p) >= 9:
                raise ValueError(f'npq должно быть больше 9')

        except ValueError as err:
            QMessageBox.warning(self, 'Ошибка!', str(err))
            return

        # self.distribution_data = poisson_data

        table = self.table
        table.setColumnCount(x_count + 1)

        for i in range(x_count + 1):
            x = round(poisson_data.X[i], 3)
            p = round(poisson_data.P[i], 3)

            x_item = QTableWidgetItem(f'{x}\t')
            p_item = QTableWidgetItem(f'{p}\t')

            # Устанавливаем флаг, чтобы сделать ячейки нередактируемыми
            x_item.setFlags(x_item.flags() & ~Qt.ItemIsEditable)
            p_item.setFlags(p_item.flags() & ~Qt.ItemIsEditable)

            table.setItem(0, i, x_item)
            table.setItem(1, i, p_item)

        # Основные харрактеристики
        self.m_label.setText(str(round(poisson_data.M, 5)))
        self.d_label.setText(str(round(poisson_data.D, 5)))
        self.sigma_label.setText(str(round(poisson_data.sigma, 5)))

        allM0 = ", ".join(map(lambda t: str(round(t, 5)), poisson_data.M0))

        self.m0_label.setText(allM0)

        plot_data = process_distribution_plot_data(poisson_data)

        # Функция распределения
        self.functionText.setPlainText(plot_data['F*'])
        self.discrete_function_graph.display(plot_data['func'], 'x', 'F*(x)', color='k')

        # Гистограмма частот и относительных частот
        self.distribution_polygon_plot.set_x_gap(None)
        self.distribution_polygon_plot.display(poisson_data.X, poisson_data.P, 'x', 'p')

    def read_manual_data(self):
        count = self.xCount.value()
        prob_success = self.probabilityOfSuccess.value()

        return process_poisson_data(n_count=count, prob=prob_success)

    def manual_input(self):
        self.xCount.valueChanged.connect(self.values_count_changed)
        self.table.setColumnCount(0)
        self.table.setColumnCount(self.xCount.value())
        self.table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.helpText.setText(
            'Укажите кол-во значений и вероятность успеха.'
        )

    def values_count_changed(self):
        self.table.setColumnCount(self.xCount.value())

    def task_name(self):
        return f"{self._task_number}. Изучение произвольного одномерного дискретного распределения с конечным множеством значений по его ряду распределения"
