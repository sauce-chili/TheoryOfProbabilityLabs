from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget
from utils.paths import resolve_path
from PyQt5 import uic


class ChiTable(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(resolve_path('ui/chi_table.ui'), self)
        self.__load_image()

    def __load_image(self):
        self.tableImg.setPixmap(QPixmap(resolve_path('res/images/lab6/chi2_table.png')))