from traceback import print_exc

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMessageBox,
    QVBoxLayout,
    QTableWidgetItem,
    QAbstractItemView,
)

from core.formulas.statistics import (
    process_continuous_data,
    process_continuous_plot_data,
    ContinuousData,
    process_continuous_intervals,
)
from utils.files import load_text_file, parse_statistic_file
from utils.paths import resolve_path
from utils.plots import *
from utils.widgets import TaskView


class Task2(TaskView):
    def __init__(self, task_number: int, parent):
        super().__init__(parent)
        self._task_number: int = task_number
        self.currentFile = None
        self.data = None

        uic.loadUi(resolve_path('ui/lab_5_task_2.ui'), self)
        self.openFile.clicked.connect(self.file_load_signal)
        self.calculateButton.clicked.connect(self.load_data)
        self.manualInput.stateChanged.connect(self.manual_input_activate)

        self.table.setRowCount(4)
        self.table.setVerticalHeaderLabels(['xi; xi+1', 'ni', 'ωi', 'ci'])
        self.prepare_plots()

    def prepare_plots(self):
        lt = QVBoxLayout()
        self.freq_polygon_plot = Polygon(self, name='Полигон частот')
        lt.addWidget(self.freq_polygon_plot, alignment=Qt.Alignment())
        self.continuous_polygon.setLayout(lt)

        lt = QVBoxLayout()
        self.relfreq_polygon_plot = Polygon(
            self, name='Полигон относительных частот'
        )
        lt.addWidget(self.relfreq_polygon_plot, alignment=Qt.Alignment())
        self.continuous_rel_polygon.setLayout(lt)

        lt = QVBoxLayout()
        self.continuous_function_graph = Function(
            self, name='Эмпирическая функция распределения'
        )
        lt.addWidget(self.continuous_function_graph, alignment=Qt.Alignment())
        self.continuous_function_plot.setLayout(lt)

        lt = QVBoxLayout()
        self.continuous_histogram_plot = Histogram(
            self, name='Гистограмма частот'
        )
        lt.addWidget(self.continuous_histogram_plot, alignment=Qt.Alignment())
        self.continuous_histogram.setLayout(lt)

        lt = QVBoxLayout()
        self.continuous_rel_histogram_plot = Histogram(
            self, name='Гистограмма относительных частот'
        )
        lt.addWidget(
            self.continuous_rel_histogram_plot, alignment=Qt.Alignment()
        )
        self.continuous_rel_histogram.setLayout(lt)

    def read_manual_data(self):
        count = self.intervalCount.value()
        data = ContinuousData([], [], [], [], 0, 0, 0, 0, 0)

        for i in range(count):
            interval = self.table.item(0, i)
            if interval is None:
                raise ValueError('Обнаружена пустая клетка интервала.')
            interval = interval.text()

            if ';' not in interval:
                raise ValueError('Неправильно указан интервал.')

            left, righ = interval.replace(' ', '').replace(',', '.').split(';')
            data.intervals.append([float(left), float(righ)])

            freq = self.table.item(1, i)
            if freq is None:
                raise ValueError('Обнаружена пустая клетка частоты.')

            data.N.append(int(freq.text()))

        return process_continuous_intervals(data)

    def load_data(self):
        interval_count = self.intervalCount.value()

        if not self.manualInput.isChecked():
            if self.data is None:
                return
            continuous_data = process_continuous_data(
                self.data, interval_count
            )
        else:
            try:
                continuous_data = self.read_manual_data()
            except ValueError as err:
                QMessageBox.warning(self, 'Ошибка!', str(err))
                return None

        plot_data = process_continuous_plot_data(continuous_data)

        table = self.table
        table.setColumnCount(interval_count)

        for i in range(interval_count):
            N = continuous_data.N[i]
            W = continuous_data.W[i]
            mid = continuous_data.middles[i]
            table.setItem(
                0,
                i,
                QTableWidgetItem(
                    f'{round(continuous_data.intervals[i][0], 3)}; '
                    f'{round(continuous_data.intervals[i][1], 3)}\t'
                ),
            )
            table.setItem(1, i, QTableWidgetItem(f'{N}\t'))
            table.setItem(2, i, QTableWidgetItem(f'{round(W, 3)}\t'))
            table.setItem(3, i, QTableWidgetItem(f'{round(mid, 3)}\t'))

        # Основные харрактеристики
        self.xv_label.setText(str(round(continuous_data.x_v, 5)))
        self.dv_label.setText(str(round(continuous_data.D_v, 5)))
        self.sigma_v_label.setText(str(round(continuous_data.sigma, 5)))
        self.s_label.setText(str(round(continuous_data.S, 5)))

        # Эмпирическая функция
        self.functionText.setPlainText(plot_data['F*'])
        self.continuous_function_graph.display(
            plot_data['func'], 'x', 'F*(x)', color='k'
        )

        # Полигон частот и относительных частот
        self.freq_polygon_plot.set_x_gap(None)
        self.relfreq_polygon_plot.set_x_gap(None)

        Xmin = continuous_data.middles[0]
        if continuous_data.middles[0] > 100:
            self.freq_polygon_plot.set_x_gap(round(Xmin * 0.9, 2))
            self.relfreq_polygon_plot.set_x_gap(round(Xmin * 0.9, 2))

        self.freq_polygon_plot.display(
            continuous_data.middles, continuous_data.N, 'xi*', 'ni'
        )
        self.relfreq_polygon_plot.display(
            continuous_data.middles,
            continuous_data.W,
            'xi*',
            'ωi',
            color='#16db16',
        )
        # Гистограмма частот и относительных частот
        bounds = list(map(lambda x: x[0], continuous_data.intervals))
        bounds.append(continuous_data.intervals[-1][1])

        self.continuous_histogram_plot.set_x_gap(None)
        self.continuous_rel_histogram_plot.set_x_gap(None)
        Xmin = continuous_data.intervals[0][0]
        if continuous_data.middles[0] > 100:
            self.continuous_histogram_plot.set_x_gap(round(Xmin - (Xmin / 4), 2))
            self.continuous_rel_histogram_plot.set_x_gap(round(Xmin - (Xmin / 4), 2))

        self.continuous_histogram_plot.display(
            bounds,
            continuous_data.h,
            continuous_data.middles,
            continuous_data.N,
            'xi*',
            'ni/h',
        )
        self.continuous_rel_histogram_plot.display(
            bounds,
            continuous_data.h,
            continuous_data.middles,
            continuous_data.W,
            'xi*',
            'ωi/h',
            color='#16db16',
        )

    def file_load_signal(self):
        self.file_input_activate()
        load_text_file(self)
        if self.currentFile:
            try:
                self.data = parse_statistic_file(self.currentFile)
                self.intervalCount.setMaximum(len(set(self.data)))
                self.load_data()
            except Exception as err:
                print_exc()
                QMessageBox.critical(self, "Возникла ошибка", str(err))

    def file_input_activate(self):
        self.manualInput.disconnect()
        self.manualInput.stateChanged.connect(self.manual_input_activate)

        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.helpText.setText(
            'В файле должны находиться числа, которые '
            'разделены пробелом или переносом строки'
        )

    def manual_input_activate(self):
        self.manualInput.disconnect()
        self.manualInput.stateChanged.connect(self.file_input_activate)

        self.intervalCount.valueChanged.connect(self.interval_count_changed)
        self.table.setColumnCount(0)
        self.table.setColumnCount(self.intervalCount.value())
        self.table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.helpText.setText(
            'Укажите количество интервалов, а после введите '
            'значения xi и ni и нажмите "Рассчитать". '
            'Границы интервалов должны разделяться ";"'
        )

    def interval_count_changed(self):
        self.table.setColumnCount(self.intervalCount.value())

    def task_name(self):
        return f"{self._task_number}. Непрерывная случайная величина"
