from PyQt5.QtGui import QPixmap

from utils.widgets import TaskView
from utils.paths import resolve_path
from utils.files import load_text_file, parse_statistic_file
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMessageBox,
    QVBoxLayout,
    QTableWidgetItem,
    QTableWidget,
    QAbstractItemView,
)

from utils.plots import *
from utils.chi_table import ChiTable
from traceback import print_exc
from scipy.stats import chi2

from core.formulas.statistics import (
    process_continuous_data,
    evenly_process_density,
    ContinuousData,
    process_continuous_intervals,
    theoretical_probability_of_evenly,
    theoretical_frequencies_of_evenly,
    evenly_chi2,
    calculate_a_in_evenly_distribution,
    calculate_b_in_evenly_distribution,
    prepare_evenly_process_density_plots
)


class Task2(TaskView):
    def __init__(self, task_number: int, parent):
        super().__init__(parent)
        self._task_number: int = task_number
        self.currentFile = None
        self.data = None
        self.chi_table = ChiTable()

        uic.loadUi(resolve_path('ui/lab_6_task_2.ui'), self)
        self.viewTable.clicked.connect(self.chi_table.show)
        self.openFile.clicked.connect(self.file_load_signal)
        self.calculateButton.clicked.connect(self.load_data)
        self.manualInput.stateChanged.connect(self.manual_input_activate)

        self.intervals_combobox.currentIndexChanged.connect(self.interval_selected)
        self.alpha.valueChanged.connect(self.significance_level_changed)

        self.table.setRowCount(7)
        self.table.setVerticalHeaderLabels(['xi; xi+1', 'ni', 'ωi', 'ci',
                                            "n'i = p_i*n", "(n'i - ni)^2",
                                            "(n'i - ni)^2 / n'i"
                                            ])
        self.__load_images()
        self.prepare_plots()

    def __load_images(self):
        self.main_parameters_formulas.setPixmap(QPixmap(resolve_path('res/images/lab6/main_parameters.png')))
        self.a_param.setPixmap(QPixmap(resolve_path('res/images/lab6/a_param.png')))
        self.b_param.setPixmap(QPixmap(resolve_path('res/images/lab6/b_param.png')))
        self.densityLabel.setPixmap(QPixmap(resolve_path('res/images/lab6/evenly_density.png')))
        self.pi_evenly.setPixmap(QPixmap(resolve_path('res/images/lab6/pi_evenly.png')))
        self.observed_value.setPixmap(QPixmap(resolve_path('res/images/lab6/observed_value.png')))

    def prepare_plots(self):
        lt = QVBoxLayout()
        self.histpolygon = PolygonHistogramContinuous(
            self, name='Гистограмма относительных частот'
        )
        lt.addWidget(self.histpolygon, alignment=Qt.Alignment())
        self.continuous_rel_histpolygon.setLayout(lt)

        lt = QVBoxLayout()
        self.density_graph = ContinuousFunction(
            self, name='Плотность распределения'
        )
        lt.addWidget(self.density_graph, alignment=Qt.Alignment())
        self.density_plot.setLayout(lt)

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

        self.continuous_data = continuous_data

        self.a = a = calculate_a_in_evenly_distribution(continuous_data.x_v, continuous_data.sigma)
        self.b = b = calculate_b_in_evenly_distribution(continuous_data.x_v, continuous_data.sigma)

        table: QTableWidget = self.table
        table.setColumnCount(interval_count)

        all_theoretical_frequences = []
        Xmin = continuous_data.intervals[0][0]
        Xmax = continuous_data.intervals[len(continuous_data.intervals) - 1][1]
        Nsum = sum(continuous_data.N)
        all_theoretical_frequences = theoretical_frequencies_of_evenly(Nsum, a, b, continuous_data.intervals)
        for i in range(interval_count):
            N = continuous_data.N[i]
            W = continuous_data.W[i]
            mid = continuous_data.middles[i]
            pi = theoretical_probability_of_evenly(continuous_data.intervals[i], Xmin, Xmax)
            theoretical_probability = all_theoretical_frequences[i] # TODO проверить не напутал ли с частотой и вероятностью
            n_square = (continuous_data.N[i] - theoretical_probability) ** 2
            chi_2 = n_square / theoretical_probability
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
            table.setItem(4, i, QTableWidgetItem(f'{round(theoretical_probability, 3)}\t'))
            table.setItem(5, i, QTableWidgetItem(f'{round(n_square, 3)}\t'))
            table.setItem(6, i, QTableWidgetItem(f'{round(chi_2, 3)}\t'))

        # Основные харрактеристики
        self.xv_label.setText(str(round(continuous_data.x_v, 5)))
        self.dv_label.setText(str(round(continuous_data.D_v, 5)))
        self.sigma_v_label.setText(str(round(continuous_data.sigma, 5)))
        self.s_label.setText(str(round(continuous_data.S, 5)))

        # График плотности распределения
        plot_data = prepare_evenly_process_density_plots(a, b, continuous_data.intervals)
        self.density_graph.display(
            plot_data, 'x', 'f*(x)', color='k'
        )

        # Точечные оценки
        self.a_label.setText(str(round(a, 5)))
        self.b_label.setText(str(round(b, 5)))
        self.significance_level_changed(self.alpha.value())

        # Гистограмма частот и относительных частот
        bounds = list(map(lambda x: x[0], continuous_data.intervals))
        bounds.append(continuous_data.intervals[-1][1])

        self.histpolygon.set_x_gap(None)
        Xmin = continuous_data.intervals[0][0]
        if continuous_data.middles[0] > 100:
            self.histpolygon.set_x_gap(round(Xmin - (Xmin / 4), 2))

        self.histpolygon.display(
            plot_data,
            bounds,
            continuous_data.h,
            continuous_data.middles,
            continuous_data.W,
            'xi*',
            'ni/nh',
        )

        self.intervals_combobox.clear()
        self.intervals_combobox.addItems(list(map(lambda x: f"[{x[0]}, {x[1]})", continuous_data.intervals)))

    def significance_level_changed(self, value):
        k = self.intervalCount.value() - 2
        if k > 0:
            alpha = value
            chi2_crit = round(chi2.ppf(1 - alpha, k), 5)
            chi2_exp = round(evenly_chi2(self.a, self.b, self.continuous_data), 5)

            self.k_label.setText(str(k))
            self.chi2_label.setText(str(chi2_crit))
            self.chi2_exp_label.setText(str(chi2_exp))

            if chi2_exp > chi2_crit:
                self.checkResult_label.setStyleSheet("color: red; font-size: 24px")
                self.checkResult_label.setText("ГИПОТЕЗА ОТВЕРГНУТА")
            else:
                self.checkResult_label.setStyleSheet("color: green; font-size: 24px")
                self.checkResult_label.setText("ГИПОТЕЗА ПРИНЯТА")

    def interval_selected(self, index):
        interval = self.continuous_data.intervals[index]
        self.prob_label.setText(str(
            round(theoretical_probability_of_evenly(interval, self.a, self.b), 5)))

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
        return f"{self._task_number}. Проверка гипотезы о равномерном распределении"
