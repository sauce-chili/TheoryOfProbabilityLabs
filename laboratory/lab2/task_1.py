from PyQt5 import uic
from PyQt5.QtGui import QPixmap

from utils.paths import resolve_path
from utils.widgets import TaskView


class Task1(TaskView):

    def __init__(self, task_number: int, parent):
        super().__init__(parent)
        self._task_number = task_number

        self.__init_ui()
        self.__bind_listeners()

    def __init_ui(self):
        uic.loadUi(resolve_path("ui/lab_2_task_2.ui"), self)
        self.__load_images()

    def __load_images(self):
        self.text_of_task.setPixmap(QPixmap(resolve_path('res/images/lab2/pics_lab_1/scheme.png')))
        self.scheme_pic.setPixmap(QPixmap(resolve_path('res/images/lab2/pics_lab_1/text_of_task.png')))
        self.formula_pic.setPixmap(QPixmap(resolve_path('res/images/lab2/pics_lab_1/formula.png')))

    def __bind_listeners(self):
        self.calculate_button.clicked.connect(self.__calculate)

    def __calculate(self):
        count_q = 5
        q1, q2, q3, q4, q5 = \
            (getattr(self, f"q{i}_count").value() for i in range(1, count_q + 1))

        probability_of_chain_break = (q1 + q4 - q1 * q4) * q3 * (q2 + q5 - q2 * q5)

        self.result.setText(str(probability_of_chain_break))

    def task_name(self):
        return f"{self._task_number}. Нахождение вероятности безотказной работы заданной схемы (или отказа схемы)"
