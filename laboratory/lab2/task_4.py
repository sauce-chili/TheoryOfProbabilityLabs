from PyQt5 import uic
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QCheckBox

from utils.paths import resolve_path
from utils.widgets import TaskView


class Task4(TaskView):
    def __init__(self, task_number: int, parent):
        super().__init__(parent)
        self._task_number: int = task_number
        uic.loadUi(resolve_path('ui/lab2_task_4.ui'), self)

        self._count_of_events = 2

        self._init_ui()
        self._compute_formulas()
        self._update_count_of_events()

    def _init_ui(self):
        self.countOfEvents.valueChanged.connect(self._update_count_of_events)
        self.h1.valueChanged.connect(self._on_spinbox_input)
        self.h2.valueChanged.connect(self._on_spinbox_input)
        self.c1.valueChanged.connect(self._compute_formulas)
        self.c2.valueChanged.connect(self._compute_formulas)
        self.all_ph.clicked.connect(self._on_checkbox_clicked)
        self.ph1.clicked.connect(self._on_checkbox_clicked)
        self.ph2.clicked.connect(self._on_checkbox_clicked)

    def task_name(self):
        return f"{self._task_number}. Формулы полной вероятности и Байеса"

    def _update_count_of_events(self):
        count = self.countOfEvents.value()

        # Adding new widgets
        for num in range(self._count_of_events + 1, count + 1, 1):
            self._add_new_event_spinbox(num)
            self._add_new_cond_probability(num)

        # Remove extra widgets
        for num in range(self._count_of_events, count, -1):
            self._remove_event_spinbox(num)
            self._remove_cond_probability(num)

        self._count_of_events = count
        self._compute_formulas()
        self.h1.valueChanged.emit(self.h1.value())

    def _add_new_cond_probability(self, num: int):
        f = QFont()
        f.setPixelSize(17)

        chb = QCheckBox(f'P(H{num}|A)')
        chb.setChecked(False)
        chb.setObjectName(f'ph{num}')
        chb.setFont(f)
        chb.clicked.connect(self._on_checkbox_clicked)
        self.scrollAreaWidgetContents_2.layout().insertWidget(num + 1, chb)

        setattr(self, f'ph{num}', chb)

    def _remove_cond_probability(self, num: int):
        chb = getattr(self, f'ph{num}')
        chb.setVisible(False)
        chb.disconnect()
        delattr(self, f'ph{num}')

    def _on_checkbox_clicked(self):
        if self.sender() is not self.all_ph:
            self.all_ph.setChecked(False)

        if self.all_ph.isChecked():
            for num in range(1, self._count_of_events + 1):
                getattr(self, f'ph{num}').setChecked(True)

        if self.sender() is self.all_ph and not self.all_ph.isChecked():
            for num in range(1, self._count_of_events + 1):
                getattr(self, f'ph{num}').setChecked(False)

        self._compute_formulas()

    def _add_new_event_spinbox(self, num: int):
        f = QFont()
        f.setPixelSize(17)

        h_spb = QDoubleSpinBox()
        h_spb.setValue(0.0)
        h_spb.setPrefix(f'P(H{num}) = ')
        h_spb.setObjectName(f'h{num}')
        h_spb.setFont(f)
        h_spb.setMaximum(1)
        h_spb.setDecimals(3)
        h_spb.setSingleStep(0.01)
        h_spb.valueChanged.connect(self._on_spinbox_input)

        c_spb = QDoubleSpinBox()
        c_spb.setValue(0.0)
        c_spb.setPrefix(f'P(A|H{num}) = ')
        c_spb.setObjectName(f'c{num}')
        c_spb.setFont(f)
        c_spb.setMaximum(1)
        c_spb.setDecimals(3)
        c_spb.setSingleStep(0.01)
        c_spb.valueChanged.connect(self._compute_formulas)

        layout = QHBoxLayout()
        layout.addWidget(h_spb)
        layout.addWidget(c_spb)

        self.scrollAreaWidgetContents.layout().insertLayout(num - 1, layout)

        setattr(self, f'layout_{num}', layout)
        setattr(self, f'c{num}', c_spb)
        setattr(self, f'h{num}', h_spb)

    def _remove_event_spinbox(self, num: int):
        spb = getattr(self, f'c{num}')
        spb.setVisible(False)
        spb.disconnect()
        spb = getattr(self, f'h{num}')
        spb.setVisible(False)
        spb.disconnect()
        delattr(self, f'layout_{num}')
        delattr(self, f'c{num}')
        delattr(self, f'h{num}')

    def _on_spinbox_input(self):
        name = self.h1
        if self.sender() is not None:
            name = self.sender().objectName()
        sender_attr = getattr(self, f"{name}")

        s = 0
        for attr in sorted(
                [
                    getattr(self, f"h{num}")
                    for num in range(1, self._count_of_events + 1)
                ],
                key=lambda x: x.value(),
        ):
            attr.setStyleSheet("")
            val = attr.value()
            attr.setMaximum(max(0, 1 - s))
            s += val

        if s + 0.0001 < 1:
            sender_attr.setStyleSheet("background-color: rgb(255, 170, 0)")

        self._compute_formulas()

    def _compute_formulas(self):
        text_arr = []
        for num in range(1, self._count_of_events + 1):
            h_spb = getattr(self, f"h{num}")
            c_spb = getattr(self, f"c{num}")
            text_arr.append(
                f"{round(h_spb.value(), 12)} · {round(c_spb.value(), 12)}"
            )
        text = ' + '.join(text_arr)
        self.total_formula_formula.setText(text)
        self.total_formula_formula_2.setText(text)

        res = str(round(eval(text.replace('·', '*')), 12))
        self.total_formula_result.setText(res)
        self.total_formula_result_2.setText(res)

        self._del_prev_bayes_formulas()
        for num in range(1, self._count_of_events + 1):
            if (
                    not self.all_ph.isChecked()
                    and not getattr(self, f'ph{num}').isChecked()
            ):
                continue

            h_spb = getattr(self, f"h{num}")
            c_spb = getattr(self, f"c{num}")
            head = f'P(H{num}|A) = P(H{num}) · P(A|H{num}) / P(A) = '
            body = f"{round(h_spb.value(), 12)} · {round(c_spb.value(), 12)} / {res}"
            try:
                r = str(round(eval(body.replace('·', '*')), 12))
            except ZeroDivisionError:
                r = '0'
            text = head + body + f" = {r}"

            label = QLabel(self)
            f = QFont()
            f.setPixelSize(18)
            label.setFont(f)
            label.setText(text)

            setattr(self, f'lab{num}', label)

            self.scrollAreaWidgetContents_8.layout().insertWidget(
                num - 1, label
            )

    def _del_prev_bayes_formulas(self):

        for num in range(1, self._count_of_events + 2):
            label = getattr(self, f'lab{num}', None)
            if label is None:
                continue
            label.setVisible(False)
            delattr(self, f'lab{num}')
