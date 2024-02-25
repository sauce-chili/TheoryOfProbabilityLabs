from PyQt5.QtWidgets import QWidget, QMainWindow


class TaskView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
    
    def task_name(self):
        return "Unnamed Task"