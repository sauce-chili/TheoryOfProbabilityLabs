
from PyQt5.QtWidgets import QWidget
from utils.paths import resolve_path
from PyQt5 import uic


class ChiTable(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(resolve_path('ui/chi_table.ui'), self)