from PyQt5.QtWidgets import QWidget, QMainWindow
class UI_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = QMainWindow()
        self.ui.setupUi(self)

        self.ui.setStyleSheet('background: black;')

class TaskView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
    
    def task_name(self):
        return "Unnamed Task"