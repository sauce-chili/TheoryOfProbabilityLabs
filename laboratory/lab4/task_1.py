from utils.widgets import TaskView
from utils.paths import resolve_path
from utils.files import load_text_file, parse_statistic_file
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QTableWidgetItem
from utils.plots import *
from traceback import print_exc
from core.formulas.statistics import *

from PyQt5.QtWidgets import (
    QMessageBox,
    QVBoxLayout,
    QTableWidgetItem,
    QAbstractItemView
)

class Task1(TaskView):
    def __init__(self, task_number: int, parent):
        super().__init__(parent)
        self._task_number: int = task_number
        self.data = None

        uic.loadUi(resolve_path('ui/lab_4_task_1.ui'), self)
        self.manual_input()
        self.calculateButton.clicked.connect(self.load_data)
        self.table.setRowCount(2)
        self.table.setVerticalHeaderLabels(['xi', 'pi'])

    def prepare_plots(self):
        lt = QVBoxLayout()
        self.discrete_function_graph = Function(self, name='Эмпирическая функция распределения')
        lt.addWidget(self.discrete_function_graph, alignment=Qt.Alignment())
        self.discrete_function_plot.setLayout(lt)

        lt = QVBoxLayout()
        self.distribution_polygon_plot = Polygon(self, name='Многоугольник распределения')
        lt.addWidget(self.distribution_polygon_plot, alignment=Qt.Alignment())
        self.distribution_polygon.setLayout(lt)

    def load_data(self):
        x_count = self.xCount.value()

        try:
            distribution_data = self.read_manual_data()
        except ValueError as err:
            QMessageBox.warning(self, 'Ошибка!', str(err))
            return None

        self.distribution_data = distribution_data

        table = self.table
        table.setColumnCount(x_count)

        if (sum(distribution_data.P) > 1.05 or sum(distribution_data.P) < 0.95):
            raise ValueError('Вероятность не равна приблизительно единице:  ' + sum(distribution_data.P))

        for i in range(x_count):
            X = distribution_data.X[i]
            P = distribution_data.P[i]
            table.setItem(0, i, QTableWidgetItem(f'{X}\t'))
            table.setItem(1, i, QTableWidgetItem(f'{P}\t'))

        # Основные харрактеристики
        self.m_label.setText(str(round(distribution_data.x_v, 5)))
        self.d_label.setText(str(round(distribution_data.D_v, 5)))
        self.sigma_label.setText(str(round(distribution_data.sigma, 5)))

        allM0 = ""
        for i in distribution_data.M0:
            allM0 += str(round(i, 5)) + ", "
        allM0 = allM0[:-2]

        self.m0_label.setText(allM0)

        # Функция распределения
        plot_data = process_discrete_plot_data
        self.functionText.setPlainText(plot_data['F'])
        self.discrete_function_graph.display(plot_data['func'], 'x', 'F*(x)', color='k')

        # Гистограмма частот и относительных частот
        plot_data = prepare_distribution_polygon_plots(distribution_data.X, distribution_data.P)
        self.density_graph.display(
            plot_data, 'x', 'f*(x)', color='k'
        )

    def read_manual_data(self):
        count = self.xCount.value()
        data = DistributionData([], [], [], 0, 0, 0)

        for i in range(count):
            x = self.table.item(0, i)
            x = x.value()

            probability = self.table.item(1, i)
            if probability is None:
                raise ValueError('Не указана вероятность для ' + str(i + 1) + '-й точки.')

            probability = probability.value()
            data.X.append(x)
            data.P.append(probability)

        return process_distribution_data(data)

    def manual_input(self):
        self.xCount.valueChanged.connect(self.values_count_changed)
        self.table.setColumnCount(0)
        self.table.setColumnCount(self.xCount.value())
        self.table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.helpText.setText(
            'Укажите количество значений, а после введите '
            'их вероятнсоти pi и нажмите "Рассчитать". '
        )

    def values_count_changed(self):
        self.table.setColumnCount(self.xCount.value())

    def task_name(self):
        return f"{self._task_number}. Изучение произвольного одномерного дискретного распределения с конечным множеством значений по его ряду распределения"