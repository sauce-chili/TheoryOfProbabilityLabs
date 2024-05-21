from utils.widgets import TaskView
from utils.paths import resolve_path
from utils.files import load_text_file, parse_statistic_file
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMessageBox,
    QVBoxLayout,
    QTableWidgetItem,
    QAbstractItemView
)
from utils.plots import *
from utils.chi_table import ChiTable
from traceback import print_exc
from scipy.stats import chi2

from core.formulas.statistics import (
    process_continuous_data,
    process_normal_density,
    ContinuousData,
    process_continuous_intervals,
    normal_theorethical_probability,
    normal_chi2
)


class Task1(TaskView):
    def __init__(self, task_number: int, parent):
        super().__init__(parent)
        self._task_number: int = task_number
        self.currentFile = None
        self.data = None
        self.chi_table = ChiTable() 

        uic.loadUi(resolve_path('ui/lab_6_task_1.ui'), self)
        self.openFile.clicked.connect(self.file_load_signal)
        self.viewTable.clicked.connect(self.chi_table.show)
        self.calculateButton.clicked.connect(self.load_data)
        self.manualInput.stateChanged.connect(self.manual_input_activate)

        self.intervals_combobox.currentIndexChanged.connect(self.interval_selected)
        self.alpha.valueChanged.connect(self.significance_level_changed)

        self.table.setRowCount(7)
        self.table.setVerticalHeaderLabels(['xi; xi+1', 'ni', 'ωi', 'ci',
                                             "n'i = p_i*n", "(n'i - ni)^2", 
                                             "(n'i - ni)^2 / n'i"
                                             ])
        self.prepare_plots()

    def prepare_plots(self):
        layout = QVBoxLayout()
        self.histpolygon = PolygonHistogramContinuous(
            self, name='Графики'
        )
        layout.addWidget(self.histpolygon, alignment=Qt.Alignment())
        self.continuous_rel_histpolygon.setLayout(layout)

        layout = QVBoxLayout()
        self.density_graph = ContinuousFunction(
            self, name='Плотность распределения'
        )
        layout.addWidget(self.density_graph, alignment=Qt.Alignment())
        self.density_plot.setLayout(layout)

    def read_manual_data(self):
        count = self.intervalCount.value()
        data = ContinuousData([], [], [], [], 0, 0, 0, 0, 0)

        for i in range(count):
            interval = self.table.item(0, i)
            if interval is None:
                raise ValueError('Не указана граница ' + str(i + 1) + '-го интервала')
            interval = interval.text()

            if ';' not in interval:
                raise ValueError('Неверно указан интервал. Отсутствует ; между границами ' + str(i + 1) + '-го интервала')
            
            left, right = interval.replace(' ', '').replace(',', '.').split(';')
            data.intervals.append([float(left), float(right)])

            freq = self.table.item(1, i)
            if freq is None:
                raise ValueError('Не указана частота для ' + str(i + 1) + '-го интервала')

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
        
        self.a = a = continuous_data.x_v
        self.sigma = sigma = continuous_data.sigma

        table = self.table
        table.setColumnCount(interval_count)

        N_total = sum(continuous_data.N)
        for i in range(interval_count):
            N = continuous_data.N[i]
            W = continuous_data.W[i]
            mid = continuous_data.middles[i]
            pi = normal_theorethical_probability(continuous_data.intervals[i], a, sigma)
            npi = pi * N_total
            n_square = (npi - continuous_data.N[i]) ** 2
            chi_2 = n_square / npi
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
            table.setItem(4, i, QTableWidgetItem(f'{round(npi, 3)}\t'))
            table.setItem(5, i, QTableWidgetItem(f'{round(n_square, 3)}\t'))
            table.setItem(6, i, QTableWidgetItem(f'{round(chi_2, 3)}\t'))

        # Основные харрактеристики
        self.xv_label.setText(str(round(continuous_data.x_v, 5)))
        self.dv_label.setText(str(round(continuous_data.D_v, 5)))
        self.sigma_v_label.setText(str(round(continuous_data.sigma, 5)))
        self.s_label.setText(str(round(continuous_data.S, 5)))

        # Эмпирическая функция
        if sigma:
            plot_data = process_normal_density(a, sigma)
            self.density_graph.display(
                plot_data, 'x', 'f*(x)', color='k'
            )

        self.a_label.setText(str(round(a, 5)))
        self.sigma_label.setText(str(round(sigma, 5)))
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
    
    def significance_level_changed(self, significance_level):
        k = self.intervalCount.value() - 3
        # k = m - 3 только для нормального распределения, у других распределений другая формула
        if k > 0 and self.sigma:
            chi2_crit = round(chi2.ppf(1 - significance_level, k), 5)
            chi2_exp = round(normal_chi2(self.intervalCount.value(), self.a, self.sigma, self.continuous_data), 5)
        
            self.k_label.setText(str(k))
            self.chi2_label.setText(str(chi2_crit))
            self.chi2_exp_label.setText(str(chi2_exp))

            if chi2_exp > chi2_crit:
                self.checkResult_label.setStyleSheet("color: red; font-size: 24px")
                self.checkResult_label.setText("ГИПОТЕЗА ОТВЕРГНУТА")
            else:
                self.checkResult_label.setStyleSheet("color: green; font-size: 24px")
                self.checkResult_label.setText("ГИПОТЕЗА НЕ ОТВЕРГНУТА")

    def interval_selected(self, index):
        interval = self.continuous_data.intervals[index]
        if self.sigma:
            self.prob_label.setText(str(
                round(normal_theorethical_probability(interval, self.a, self.sigma), 5)))
    
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
        return f"{self._task_number}. Проверка гипотезы о нормальном распределении"
