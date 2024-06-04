from utils.widgets import TaskView
from utils.paths import resolve_path
from utils.files import load_text_file, parse_statistic_file
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QTableWidgetItem
from utils.plots import *
from traceback import print_exc

from core.formulas.statistics import process_discrete_data, process_discrete_plot_data

class Task1(TaskView):
    def __init__(self, task_number: int, parent):
        super().__init__(parent)
        self._task_number: int = task_number
        self.currentFile = None
        self.data = None

        uic.loadUi(resolve_path('ui/lab_5_task_1.ui'), self)
        self.openFile.clicked.connect(self.file_load_signal)
        self.table.setRowCount(3)
        self.table.setVerticalHeaderLabels(['xi', 'ni', 'ωi'])
        self.prepare_plots()

    def prepare_plots(self):
        lt = QVBoxLayout()
        self.freq_polygon_plot = Polygon(self, name='Полигон частот')
        lt.addWidget(self.freq_polygon_plot, alignment=Qt.Alignment())
        self.freq_polygon.setLayout(lt)

        lt = QVBoxLayout()
        self.relfreq_polygon_plot = Polygon(self, name='Полигон относительных частот')
        lt.addWidget(self.relfreq_polygon_plot, alignment=Qt.Alignment())
        self.rel_freq_polygon.setLayout(lt)

        lt = QVBoxLayout()
        self.discrete_function_graph = Function(self, name='Эмпирическая функция распределения')
        lt.addWidget(self.discrete_function_graph, alignment=Qt.Alignment())
        self.discrete_function_plot.setLayout(lt)

    def file_load_signal(self):
        load_text_file(self)

        if not self.currentFile:
            return

        try:
            self.data = parse_statistic_file(self.currentFile)
            discrete_data = process_discrete_data(self.data)
            plot_data = process_discrete_plot_data(discrete_data)
            k = len(discrete_data.X)
            table = self.table
            table.setColumnCount(k)

            for i in range(k):
                N = list(discrete_data.x_n.values())
                W = list(discrete_data.x_w.values())
                table.setItem(0, i, QTableWidgetItem(str(discrete_data.X[i]) + '\t'))
                table.setItem(1, i, QTableWidgetItem(str(N[i]) + '\t'))
                table.setItem(2, i, QTableWidgetItem(str(round(W[i], 3)) + '\t'))

            table.resizeColumnsToContents()

            # Основные харрактеристики

            self.varSeries.setText("; ".join(map(lambda x: str(x).replace(".", ","), sorted(self.data))))
            self.xv_label.setText(str(round(discrete_data.x_v, 5)))
            self.dv_label.setText(str(round(discrete_data.D_v, 5)))
            self.sigma_v_label.setText(str(round(discrete_data.sigma, 5)))
            self.s_label.setText(str(round(discrete_data.S, 5)))

            # Эмпирическая функция
            self.functionText.setPlainText(plot_data['F*'])
            self.discrete_function_graph.display(plot_data['func'], 'x', 'F*(x)', color='k')

            # Полигон частот и относительных частот
            self.freq_polygon_plot.set_x_gap(None)
            self.relfreq_polygon_plot.set_x_gap(None)
            if discrete_data.X[0] > 100:
                self.freq_polygon_plot.set_x_gap(round(discrete_data.X[0] - (discrete_data.X[0] / 4), 2))
                self.relfreq_polygon_plot.set_x_gap(round(discrete_data.X[0] - (discrete_data.X[0] / 4), 2))
            self.freq_polygon_plot.display(discrete_data.X, discrete_data.x_n.values(), 'xi', 'ni')
            self.relfreq_polygon_plot.display(discrete_data.X, discrete_data.x_w.values(), 'xi', 'ωi',
                                              color='#16db16')
        except Exception as e:
            print_exc()
            QMessageBox.critical(self, "Возникла ошибка", str(e))

    def task_name(self):
        return f"{self._task_number}. Дискретная случайная величина"
